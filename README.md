# README

Steps to setting up python environment in vscode

1. create yml file with all the appropriate libraries you will use
2. open anaconda launch anaconda powershell prompt
3. cd to folder with yml file
4. run `mamba env create -f pyenv.yml`
5. wait a bit for anaconda to create the environment
6. make a project folder in github directory
7. open anaconda and select `py_env` from the list and wait for it to load
8. go to home tab and launch vscode
9. open project folder in vscode
10. ctrl + shift + P to get to command palette and then "Python: Select Interpreter" to set the environment by selecting the environment you just created
11. should work fine now! (can see in the terminal that the env is set)
12. if you need to open powershell, be sure to launch it from the anaconda so the environment is set approporiately (note that you may have to install it if it's not available by default and then launch)

Note to self: need to create new text (.gitignore) file manually in file explorer b/c touch doesn't work in powershell.