# Link Shell Extension

> 原项目: [schinagl/link-shell-extension](https://gitlab.com/schinagl/link-shell-extension)  
> 本仓库为上游代码的镜像/存档分支

A Windows shell extension that supports creating and managing **hardlinks**, **junctions**, and **symbolic links** from the context menu. Originally created by **Hermann Schinagl** in 1999.

## Projects

| Project | Description |
|---------|-------------|
| **HardlinkShellExt.dll** | Windows Shell Extension (context menu) |
| **LSEConfig.exe** | Configuration tool |
| **LSEUacHelper.exe** | UAC elevation helper |
| **ln.exe** | Command-line hardlink/junction/symlink tool |
| **Dupemerge.exe** | Duplicate file merge tool |
| **xdel.exe** | Extended delete tool |
| **du.exe** | Disk usage tool (internal) |
| **TimeStamp.exe** | Timestamp tool (internal, used for ln.exe testing) |
| **Where.exe** | File location tool (internal) |

## Building

1. Open **link.sln** in Visual Studio 2017
2. Recompile in all configurations

## Testing

- Configure a profile in `HardlinkExtension/Settings.bat` for your machine
- Run `ln/LnAllTest.bat` (~15 minutes)
- Compare `LnTest_Current.txt` with `LnTest_Good.txt`

## Install Media

Run `BuildWorld.bat` to create install media. Edit the version number in the script first.

## License

Binary license: Free to use and distribute.  
Source license: To be determined (GPL-style planned).
