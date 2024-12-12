// npm install crypto

const crypto = require("crypto");

function verifySignature(body, signature, publicKey) {
    /* @param {body} string - JSON string
    @param {signature} string - base64 encoded sign
    @param {publicKey} string - base64 encoded server's public key */
    if (!signature) return false;

    const b64decode = data => Buffer.from(data, "base64");
    const publicKeyString = b64decode(publicKey).toString("utf-8");

    const digest = crypto.createHash("sha256").update(Buffer.from(body)).digest();
    const isVerified = crypto.verify(
        "sha256",
        digest,
        {
            key: publicKeyString,
            padding: crypto.constants.RSA_PKCS1_PADDING,
        },
        b64decode(signature),
    );

    return isVerified;
}
