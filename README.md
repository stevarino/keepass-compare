# KeePass Compare

Console  application to compare two KeePass Database files. Supports both KeePassX and KeePass2 files (v3 and v4). Runs under both Python 2 and 3.

## Features

 - Detects group and item additions and deletions.
 - Detects when groups and items have been moved.
 - Detects when names, passwords, and other properties are changed.
 - Can compare by UUID (more reliable) or path (more flexible).

## Installation

It's recommended to build this using a virtual environment. The instructions for this are typically specific to your platform and desired python version, so I would recommend checking with Google on how to accomplish this.

Once a virtual environment is created and activated, prerequisites can be installed as follows:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line:

```bash
python main.py file1 file2
```
### Optional Arguments:

| Flag | Long | Description |
| - | - | - |
| -h | | Help
| -p | --password | Shared password for both files
| -p1 | --password1 | Password for the first file
| -p2 | --password2 | Password for the second file
| | --compare | Change comparison mode (uuid or path, default is uuid)

*Note: if no passwords are given, passwords will be requested via stdin securely through the getpass module.*

## Example

Two sample databases have been included in the repository as an example. The password for both files is "*my_password123!*" (without quotes). Functionality can be viewed as follows:

```bash
python main.py sample.kdbx sample2.kdbx
Passsword for file "sample.kdbx"
Password:
Passsword for file "sample2.kdbx" (press enter to reuse the first password)
Password:

-/sample/Deleted Key
    Removed
!/sample/Homebanking/
    Notes field changed.
+/sample/New Key
    Added
!/sample/Renamed Group/
    Name field changed.
+/sample/Renamed Group/foo/
    Added
+/sample/Renamed Group/foo/bar/
    Added
+/sample/Renamed Group/foo/bar/baz
    Added
!/sample/Sample Entry
    UserName string modified.
    Password string modified.
!/sample/Sample Entry #2
    Tags field changed.
    Notes string added.
    New String string added.
+/sample/Sample Entry - Copy
    Added
!/sample/Windows/general key
    Changed parents.  
```
A second example showing the password flag and changing the comparison method. Notice that the 'changed parents' modification changed to a remove/addition, as did the renaming. However this can be preferred if the databases are built from scratch and not simply copies.
```bash
python main.py sample.kdbx sample2.kdbx -p my_password123! --compare path

-/sample/Deleted Key
    Removed
-/sample/General/general key
    Removed
!/sample/Homebanking/
    Notes field changed.
+/sample/New Key
    Added
+/sample/Renamed Group/
    Added
+/sample/Renamed Group/foo/
    Added
+/sample/Renamed Group/foo/bar/
    Added
+/sample/Renamed Group/foo/bar/baz
    Added
!/sample/Sample Entry
    UserName string modified.
    Password string modified.
!/sample/Sample Entry #2
    Tags field changed.
    Notes string added.
    New String string added.
+/sample/Sample Entry - Copy
    Added
+/sample/Windows/general key
    Added
-/sample/eMail/
    Removed
```

