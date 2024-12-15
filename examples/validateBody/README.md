# Example: Response Body Validation

This code validates server's response. It checks:
    - the keys `server_info.request_id` and `server_info.created_at` exist;
    - `server_info.created_at` value is in acceptable range;
    - `server_info.request_id` value is a match to UUID v4 syntax.

## Usage
1. Create BAS function named `validateBody` and checked `return` value (`Has return value: yes`). The function should accept the following arguments:
    - `body` (`Type: StringOrExpression`): the server's response body;
    - `dateDifference` (`Type: StringOrExpression`): maximum difference between server's `created_date` value and current date. String with the mask `<Integer><s|m|h|d>`. Examples:
        -- `10s`: 10 seconds;
        -- `10m`: 10 minutes;
        -- `10h`: 10 hours;
        -- `10d`: 10 days.
2. Create the actions `Get function parameter` for all received arguments inside the function (`param` -> `[[BAS_VARIABLE]]`):
    - `body` -> `[[BODY]]`;
    - `dateDifference` -> `[[DATE_DIFFERENCE]]`.
3. Create an `Execute code` action and insert the code from [validateBody.js](validateBody.js).
4. Call `validateBody` function with received `body`, from server's response and `dateDifference` string. The obtained result will be a boolean type (`true` - server's response is valid, `false` - not valid).
