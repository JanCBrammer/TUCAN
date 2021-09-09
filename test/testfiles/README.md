# File structure

This directory contains a molecule dataset for test purposes.

Each molecule has it's own sub-directory, which is named `<molecule-name>` (omit `<` and `>`).

Each sub-directory contains at minimium a molfile named `<molecule-name>.mol`.

Additionally, a sub-directory can contain metadata in a plain-text file. The metadata file
should be named `<molecule-name>_metadata.txt` and can contain references etc.. (TODO: specify fields and format).

Finally, a sub-directory can contain a molecular drawing called `<molecule-name>_drawing.jpeg` (TODO: specify file format?).

# Adding molecules

## Directly from GitHub via the browser (requires account with write access)
* In your browser go to the `test/testfiles` directory.
* Click `Add file` -> `Upload file` in the upper right corner.
* You can now drag-and-drop, or manually upload your files. Note that you cannot upload a sub-directory directly. A bot takes care of creating a sub-directory for your files and moving them there (TODO: implement GH Action for this using `format_testfiles_dir.sh`).
* Optionally, you can write a commit message.
* Finally, click the green `Commit changes` button on the lower left.

## Pushing to GitHub (requires account with write access)
Push one or multiple molecule sub-directories to `test/testfiles` as part of your regular git workflow.
