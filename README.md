[Language Server Protocol](https://github.com/Microsoft/language-server-protocol) for [Robot Framework](https://robotframework.org/)
=======

Requirements
-------------

Python 2.7 or Python 3.5+ and pip.


Installing
-----------

Right now `robotframework-lsp` can be installed as a `.vsix` into VSCode.

It can be downloaded from the latest `Deploy Extension` in [Robotframework-lsp Github Actions](https://github.com/robocorp/robotframework-lsp/actions).

See: [Install from a vsix](https://code.visualstudio.com/docs/editor/extension-gallery#_install-from-a-vsix) for details installing a `.vsix` into VSCode.


Developing
-----------

Install NodeJs (https://nodejs.org/en/) -- make sure that `node` and `npm` are in the `PATH`.

Install Yarn (https://yarnpkg.com/) -- make sure that `yarn` in in the `PATH`.

Download the sources, head to the root directory (where `package.json` is located)
and run: `yarn install`.

After this step, it should be possible to open the `roboframework-lsp` folder in VSCode and launch
`Extension: Roboframework-lsp` to have a new instance of VSCode with the loaded extension.


Building a VSIX locally
------------------------

To build a VSIX, follow the steps in https://code.visualstudio.com/api/working-with-extensions/publishing-extension. 


License: MIT
-----------------


Acknowledgements:
-----------------

The basic language server protocol implementation is based on:

https://github.com/palantir/python-jsonrpc-server

https://github.com/palantir/python-language-server
