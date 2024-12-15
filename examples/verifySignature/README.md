# Example: Signature Verification

Signature verification is a crucial part of protecting a script from various attacks, such as server address spoofing or replay attacks. Unfortunately, BAS has significant vulnerabilities that prevent 100% protection. Typically, the `crypto` library in `Node.js` is used for RSA signature verification. However, in BAS, accessing the `Node.js` code is relatively easy, even in a compiled script.

### Solution

To enhance security, important checks should be moved to the `Execute code` action, leaving only complex calculations in `Node.js` that are difficult or nearly impossible to implement in native JavaScript.

## Usage

1. Create BAS function named `isSignatureValid` and checked `return` value (`Has return value: yes`). The function should accept the following arguments:
    - `body` (`Type: StringOrExpression`): the server's response body;
    - `publicKey` (`Type: StringOrExpression`): the public key;
    - `signature` (`Type: StringOrExpression`): the `x-signature` header.
2. Create the actions `Get function parameter` for all received arguments inside the function (`param` -> `[[BAS_VARIABLE]]`):
    - `body` -> `[[BODY]]`;
    - `publicKey` -> `[[PUBLIC_KEY]]`;
    - `signature` -> `[[SIGNATURE]]`.
3. Create an `Execute code` action and insert the code from [1-beginVerifySignatureExecuteCode.js](1-beginVerifySignatureExecuteCode.js). This code parses the public key and sets the input for Node.js computation.
4. Create a `Node` action and insert the code from [2-verifySignatureNode.js](2-verifySignatureNode.js). This code performs calculations based on the prepared data.
5. Create an `Execute code` action and insert the code from [3-finalVerifySignatureExecuteCode.js](3-finalVerifySignatureExecuteCode.js). This code receives the results of the computation, performs a final signature check and returns the result from the BAS function.
6. Call `isSignatureValid` function with received `body`, `signature` from server's response and `publicKey`. The obtained result will be a boolean type (`true` - signature is valid, `false` - signature is not valid).

## Security

For security reasons, the functions are obfuscated, though this does not eliminate the possibility of deobfuscating the code.
