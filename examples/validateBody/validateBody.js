const response = JSON.parse([[BODY]]);

const parseDate = function(dateString) {
    const formattedDate = dateString.slice(0, 23) + 'Z';
    const parts = formattedDate.split(/[-T:.Z]/);
    return new Date(
        Date.UTC(
            parseInt(parts[0]),
            parseInt(parts[1]) - 1,
            parseInt(parts[2]),
            parseInt(parts[3]),
            parseInt(parts[4]),
            parseInt(parts[5]),
            parseInt(parts[6]) || 0
        )
    );
};

const parseDateInput = function(dateString) {
    const isValid = /\^d+[s|m|h|d]$/.test(dateString);
    if (!isValid) throw new Error('dateDifference is invalid');

    const format = dateString.slice(-1);
    const value = parseInt(/^\d+/.exec(dateString)[0], 10);
    var result;
    switch(format) {
      case 's':
        result = value * 1000;
        break;
      case 'm':
        result = value * 60000;
        break;
      case 'h':
        result = value * 3600000;
        break;
      case 'd':
        result = value * 86400000;
        break;
      default:
        throw new Error('Invalid dateDifference format. Expected end of string is "s", "m", "h" or "d".')
    }
    return result;
};

const isDateExpired = function(createdAt, maxDifference) {
    const date = new Date();
    const serverDate = new Date(parseDate(createdAt));
    return (date - serverDate) > parseDateInput(maxDifference);
};

const isUUIDv4Valid = function(str) {
    const regex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return regex.test(str);
};

if (
    !response.server_info
    || !response.server_info.request_id
    || !response.server_info.created_at
) {
    _function_return(false);
}

if (isDateExpired(response.server_info.created_at, [[DATE_DIFFERENCE]])) {
    _function_return(false);
}
if (!isUUIDv4Valid(response.server_info.request_id)) {
    _function_return(false);
}
_function_return(true);