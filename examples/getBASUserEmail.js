/*
1. Create function named "getBasUserEmail" with returned value.
This function returns user's email if found, otherwise `null`
when running in compiled script.
2. Make sure Path module is installed.
Create action `Path` -> `Path to project directory` with returned value as `PROJECT_DIRECTORY`
3. Place this code to `Execute code` action inside this function.

Conclusion: your function "getBasUserEmail" should include 2 actions:
- path to project directory that returns `PROJECT_DIRECTORY` variable;
- `Execute code` action with the following code.
*/


native_async(
    "filesystem",
    "search",
    JSON.stringify({
        folder: VAR_PROJECT_DIRECTORY + "/appsremote",
        mask: "settings.ini",
        contains: "",
        include_folders: false,
        include_files: true,
        recursive: true,
    })
)!
const settingsFiles = JSON.parse(_result())["d"];

const path = settingsFiles.length ? settingsFiles[0] : null;
if (!path) _function_return(null);
const settingsData = native(
    "filesystem",
    "readfile",
    JSON.stringify({
        value: path,
        base64: false,
        from: 0,
        to: 0
    })
);
settingsData.split(/\r\n/g).forEach(function(line) {
    var data = line.split("=");
    if (data[0] === "email") _function_return(data[1]);
})
_function_return(null);
