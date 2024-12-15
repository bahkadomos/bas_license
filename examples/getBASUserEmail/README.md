# Example: Get BAS User Email
This code allows you to automatically obtain the user's email from the BAS script.

## Usage
1. Create function named `getBasUserEmail` with returned value. This function returns user's email if found, otherwise `null` when running in compiled script.
2. Make sure Path module is installed. Create action `Path` -> `Path to project directory` with returned value as `PROJECT_DIRECTORY`.
3. Create an `Execute code` action and insert the code from [getBASUserEmail.js](getBASUserEmail.js).
