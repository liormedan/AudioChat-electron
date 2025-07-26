(.venv) PS C:\Audio-Chat-main\Audio-Chat-qt> cd elctron-app
cd : Cannot find path 'C:\Audio-Chat-main\Audio-Chat-qt\elctron-app' because it does not exist.
At line:1 char:1
+ cd elctron-app
+ ~~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (C:\Audio-Chat-m...-qt\elctron-app:String) [Set-Location], ItemNotFoundException
    + FullyQualifiedErrorId : PathNotFound,Microsoft.PowerShell.Commands.SetLocationCommand
 
(.venv) PS C:\Audio-Chat-main\Audio-Chat-qt> cd electron-app
(.venv) PS C:\Audio-Chat-main\Audio-Chat-qt\electron-app> npm run package 

> audio-chat-studio-electron@1.0.0 package
> npm run build && electron-builder       


> audio-chat-studio-electron@1.0.0 build
> npm run build:renderer && npm run build:main


> audio-chat-studio-electron@1.0.0 build:renderer
> vite build

The CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.
vite v5.4.19 building for production...
✓ 1733 modules transformed.
../../dist/renderer/index.html                   0.80 kB │ gzip:  0.43 kB
../../dist/renderer/assets/index-D_OnQXjL.css   25.86 kB │ gzip:  5.67 kB
../../dist/renderer/assets/index-Cw2yB0q4.js   124.03 kB │ gzip: 40.50 kB
../../dist/renderer/assets/vendor-nf7bT_Uh.js  140.87 kB │ gzip: 45.26 kB
✓ built in 4.75s

> audio-chat-studio-electron@1.0.0 build:main
> tsc -p tsconfig.main.json

  • electron-builder  version=24.13.3 os=10.0.19045
  • loaded configuration  file=package.json ("build" field)
  • writing effective config  file=release\builder-effective-config.yaml
  • packaging       platform=win32 arch=x64 electron=28.3.3 appOutDir=release\win-unpacked
  • default Electron icon is used  reason=application icon is not set
  • downloading     url=https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z size=5.6 MB parts=1
  • downloaded      url=https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z duration=1.231s
  ⨯ cannot execute  cause=exit status 2
                    out=
    7-Zip (a) 21.07 (x64) : Copyright (c) 1999-2021 Igor Pavlov : 2021-12-26

    Scanning the drive for archives:
    1 file, 5635384 bytes (5504 KiB)

    Extracting archive: C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\141393783.7z
    --
    Path = C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\141393783.7z
    Type = 7z
    Physical Size = 5635384
    Headers Size = 1492
    Method = LZMA2:24m LZMA:20 BCJ2
    Solid = +
    Blocks = 2


    Sub items Errors: 2

    Archives with Errors: 1

    Sub items Errors: 2

                    errorOut=ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\141393783\darwin\10.12\lib\libcrypto.dylib
    ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\141393783\darwin\10.12\lib\libssl.dylib

                    command='C:\Audio-Chat-main\Audio-Chat-qt\electron-app\node_modules\7zip-bin\win\x64\7za.exe' x -bd 'C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\141393783.7z' '-oC:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\141393783'
                    workingDir=C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign
  • Above command failed, retrying 3 more times
  • downloading     url=https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z size=5.6 MB parts=1
  • downloaded      url=https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z duration=1.211s
  ⨯ cannot execute  cause=exit status 2
                    out=
    7-Zip (a) 21.07 (x64) : Copyright (c) 1999-2021 Igor Pavlov : 2021-12-26

    Scanning the drive for archives:
    1 file, 5635384 bytes (5504 KiB)

    Extracting archive: C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\135327287.7z
    --
    Path = C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\135327287.7z
    Type = 7z
    Physical Size = 5635384
    Headers Size = 1492
    Method = LZMA2:24m LZMA:20 BCJ2
    Solid = +
    Blocks = 2


    Sub items Errors: 2

    Archives with Errors: 1

    Sub items Errors: 2

                    errorOut=ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\135327287\darwin\10.12\lib\libcrypto.dylib
    ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\135327287\darwin\10.12\lib\libssl.dylib

                    command='C:\Audio-Chat-main\Audio-Chat-qt\electron-app\node_modules\7zip-bin\win\x64\7za.exe' x -bd 'C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\135327287.7z' '-oC:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\135327287'
                    workingDir=C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign
  • Above command failed, retrying 2 more times
  • downloading     url=https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z size=5.6 MB parts=1
  • downloaded      url=https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z duration=1.239s
  ⨯ cannot execute  cause=exit status 2
                    out=
    7-Zip (a) 21.07 (x64) : Copyright (c) 1999-2021 Igor Pavlov : 2021-12-26

    Scanning the drive for archives:
    1 file, 5635384 bytes (5504 KiB)

    Extracting archive: C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\217346271.7z
    --
    Path = C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\217346271.7z
    Type = 7z
    Physical Size = 5635384
    Headers Size = 1492
    Method = LZMA2:24m LZMA:20 BCJ2
    Solid = +
    Blocks = 2


    Sub items Errors: 2

    Archives with Errors: 1

    Sub items Errors: 2

                    errorOut=ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\217346271\darwin\10.12\lib\libcrypto.dylib
    ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\217346271\darwin\10.12\lib\libssl.dylib

                    command='C:\Audio-Chat-main\Audio-Chat-qt\electron-app\node_modules\7zip-bin\win\x64\7za.exe' x -bd 'C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\217346271.7z' '-oC:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\217346271'
                    workingDir=C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign
  • Above command failed, retrying 1 more times
  • downloading     url=https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z size=5.6 MB parts=1
  • downloaded      url=https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z duration=960ms
  ⨯ cannot execute  cause=exit status 2
                    out=
    7-Zip (a) 21.07 (x64) : Copyright (c) 1999-2021 Igor Pavlov : 2021-12-26

    Scanning the drive for archives:
    1 file, 5635384 bytes (5504 KiB)

    Extracting archive: C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\815322783.7z
    --
    Path = C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\815322783.7z
    Type = 7z
    Physical Size = 5635384
    Headers Size = 1492
    Method = LZMA2:24m LZMA:20 BCJ2
    Solid = +
    Blocks = 2


    Sub items Errors: 2

    Archives with Errors: 1

    Sub items Errors: 2

                    errorOut=ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\815322783\darwin\10.12\lib\libcrypto.dylib
    ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\815322783\darwin\10.12\lib\libssl.dylib

                    command='C:\Audio-Chat-main\Audio-Chat-qt\electron-app\node_modules\7zip-bin\win\x64\7za.exe' x -bd 'C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\815322783.7z' '-oC:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign\815322783'
                    workingDir=C:\Users\liorm\AppData\Local\electron-builder\Cache\winCodeSign
  • Above command failed, retrying 0 more times
(.venv) PS C:\Audio-Chat-main\Audio-Chat-qt\electron-app> 