# OctoPrint M73 ETA Override

Plugin that overrides OctoPrint ETA to values from last M73 gcode sent to the printer.

PrusaSlicer is able to calculate print estimates very accurately. Those estimates get injected into generated gcode as [M73 gcode](https://marlinfw.org/docs/gcode/M073.html) commands. This plugin reads the injected information to override what OctoPrint uses as default to calculate estimates. Improved estimates are displayed in OctoPrint, your printer display and in your favorite OctoPrint client.

This plugin will also work with other slicers that inject M73 gcode commands while slicing your STL files to produce gcode.

## Why this fork exists

This fork builds on the upstream `1.0.4` release and is versioned `1.0.4.post2`. It contains two updates needed for reliable ETA reporting on newer OctoPrint installations:

1. **Reload-safe print-time estimation (`1.0.4.post1`).** OctoPrint can reload a plugin module while still holding a reference to an estimator created from the previous module instance. The original `super(M73PrintTimeEstimator, self)` calls can then fail with `TypeError: super(type, obj): obj must be an instance or subtype of type`. This fork calls the `PrintTimeEstimator` base methods directly, avoiding that reload-related crash.

2. **Slicer ETA during file analysis (`1.0.4.post2`).** The original plugin updates the ETA only after OctoPrint starts sending `M73` commands to the printer. This fork also scans an uploaded G-code file for its first `M73 ... R<minutes>` command and saves that value as `estimatedPrintTime`, allowing OctoPrint to show the slicer's estimate before printing begins.

If a file does not contain a usable `M73 R` value, OctoPrint's normal estimate remains unchanged.

## Firmware

Prusa printers will display M73 estimates without any modifications. Printers that run on Marlin firmware might require their firmware to be properly configured to display M73 ETA on the printer display. If you are using Marlin 2.0.x then you will need to:
1. Uncomment #define SHOW_REMAINING_TIME in Configuration_adv.h
1. Uncomment #define USE_M73_REMAINING_TIME in Configuration_adv.h

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/alvst/OctoPrint-M73ETAOverride/archive/refs/heads/master.zip


## Configuration

No configuration required. Just install plugin and it will start to overriding OctoPrint ETA with last M73 gcode.

Please note that if printer is starting (heating or leveling bed) ETA will show less than one minute.

## Credits

This plugin was originally developed by Jakub Furman. It was no longer being maintained so I took ownership/forked to keep it alive.
