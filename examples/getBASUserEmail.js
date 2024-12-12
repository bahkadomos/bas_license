// Create function named "getBasUserEmail" with returned value
// and place this code to "Execute code" action inside this function.
// This function returns user's email if found, otherwise `null`,
// when running in compiled script.

// Path to project directory.
// Requires Path module to be installed.
const projectDirectory = project_directory();

native_async(
    "filesystem",
    "search",
    JSON.stringify({
        folder: projectDirectory + "/appsremote",
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
    if (data.length > 1 && data[0] === "email") _function_return(data[1]);
})

_function_return(null);
