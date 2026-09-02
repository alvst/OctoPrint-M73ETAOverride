from __future__ import absolute_import
import io
import octoprint.plugin
import re
from octoprint.filemanager.analysis import GcodeAnalysisQueue
from octoprint.printer.estimation import PrintTimeEstimator

m73time = None

class M73ETA(octoprint.plugin.OctoPrintPlugin,octoprint.plugin.RestartNeedingPlugin,octoprint.plugin.ReloadNeedingPlugin):
  def handle_m73(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
    global m73time
    if gcode and gcode == "M73":
      m = re.search('(?<=R)\w+', cmd)
      if m:
        m73time = m.group(0)

  def get_update_information(self):
    return dict(
        m73etaoverride=dict(
            displayName=self._plugin_name,
            displayVersion=self._plugin_version,

            type="github_release",
            current=self._plugin_version,
            user="gdombiak",
            repo="OctoPrint-M73ETAOverride",

            pip="https://github.com/gdombiak/OctoPrint-M73ETAOverride/archive/{target}.zip"
        )
    )

class M73PrintTimeEstimator(PrintTimeEstimator):
  def __init__(self, job_type):
    # Plugin reloads can leave this method bound to an older class while the
    # module-level class name points to a new one. Avoid ``super(Class, self)``
    # so estimator creation remains valid across that reload boundary.
    PrintTimeEstimator.__init__(self, job_type)

  def estimate(self, progress, printTime, cleanedPrintTime, statisticalTotalPrintTime, statisticalTotalPrintTimeType):
    global m73time

    if m73time == None:
      return PrintTimeEstimator.estimate(self, progress, printTime, cleanedPrintTime, statisticalTotalPrintTime, statisticalTotalPrintTimeType)

    estimates = 60 * int(m73time)
    return estimates, "estimate"

def m73_create_estimator_factory(*args, **kwargs):
    return M73PrintTimeEstimator


class M73AnalysisQueue(GcodeAnalysisQueue):
  """Use the slicer's initial M73 remaining-time value for file metadata."""
  _m73_remaining_time_pattern = re.compile(r"^\s*M73\b.*?\bR(?P<minutes>\d+)")

  def _do_analysis(self, high_priority=False):
    results = GcodeAnalysisQueue._do_analysis(self, high_priority=high_priority)
    if not results:
      return results

    try:
      with io.open(self._current.absolute_path, encoding="utf-8", errors="replace") as gcode:
        for line in gcode:
          m = self._m73_remaining_time_pattern.match(line)
          if m:
            results["estimatedPrintTime"] = int(m.group("minutes")) * 60
            break
    except (IOError, OSError) as error:
      self._logger.warning(
          "Could not read M73 estimate from %s: %s", self._current.absolute_path, error
      )

    return results


def m73_gcode_analysis_queue(*args, **kwargs):
  return dict(gcode=lambda finished_callback: M73AnalysisQueue(finished_callback))

__plugin_name__ = "M73 ETA Override"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
  global __plugin_implementation__
  __plugin_implementation__ = M73ETA()

  global __plugin_hooks__
  __plugin_hooks__ = {
    "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.handle_m73,
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
    "octoprint.printer.estimation.factory": m73_create_estimator_factory,
    "octoprint.filemanager.analysis.factory": m73_gcode_analysis_queue
  }
