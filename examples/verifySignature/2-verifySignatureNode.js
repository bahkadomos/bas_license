const k = b;
(function (c, d) {
    const j = b, e = c();
    while (!![]) {
        try {
            const f = parseInt(j(0xd1)) / (0x1a3 * 0x7 + -0x13d0 + -0x42e * -0x2) + -parseInt(j(0xca)) / (-0x1b5d + -0x39 * -0x7 + 0x19d0) * (-parseInt(j(0xc4)) / (0x7a * -0x2 + 0x7f * 0x33 + 0xb2 * -0x23)) + -parseInt(j(0xd6)) / (0x1903 * -0x1 + -0x1 * 0x1088 + 0x298f) + -parseInt(j(0xcf)) / (0xcf6 + -0x1 * -0xc5 + 0x27 * -0x5a) + parseInt(j(0xd5)) / (0x1aff + -0x1512 * 0x1 + -0x5e7) + -parseInt(j(0xc6)) / (-0x5 * -0x299 + -0x5b5 + -0x741) * (-parseInt(j(0xd3)) / (0x1733 * -0x1 + 0x66e + 0xfd * 0x11)) + parseInt(j(0xce)) / (0x11b0 * 0x2 + -0x52c * 0x4 + -0xea7) * (parseInt(j(0xd8)) / (0x3 * 0xbc5 + -0x371 * -0x1 + 0x2 * -0x135b));
            if (f === d)
                break;
            else
                e['push'](e['shift']());
        } catch (g) {
            e['push'](e['shift']());
        }
    }
}(a, -0x3f097 * -0x1 + -0x35 * 0x1a9a + 0x4b820));
function b(c, d) {
    const e = a();
    return b = function (f, g) {
        f = f - (-0x4d9 + -0x1f * 0xa2 + 0x1 * 0x193b);
        let h = e[f];
        return h;
    }, b(c, d);
}
const crypto = require(k(0xd0));
function computeSHA256(c) {
    const l = k, d = crypto[l(0xd2)](l(0xcd));
    d[l(0xcb)](c, l(0xc5));
    const e = d[l(0xc7)]();
    return Array[l(0xd4)](e);
}
function bytesToBigInt(c) {
    const m = k;
    let d = 0x0n;
    for (let e = 0xa9e * -0x2 + -0x151d + 0x2a59; e < c[m(0xc9)]; e++) {
        d = d << 0x8n | BigInt(c[e]);
    }
    return d;
}
function modPowBI(c, d, f) {
    let g = 0x1n, h = c % f, i = d;
    while (i > 0x0n) {
        (i & 0x1n) === 0x1n && (g = g * h % f), i >>= 0x1n, h = h * h % f;
    }
    return g;
}
function bigIntToBytes(c, d) {
    const n = k;
    let e = c[n(0xd9)](-0x36 * -0x13 + -0x12d6 * 0x1 + 0xee4);
    if (e[n(0xc9)] % (-0x2 * -0x125e + 0x2e * -0x7f + -0x4 * 0x37a) !== -0x2524 + 0x22 * 0x7f + 0x1446)
        e = '0' + e;
    let f = [];
    for (let g = -0x110c + -0x16c0 + 0x27cc; g < e[n(0xc9)]; g += -0x1 * 0x99 + -0x2 * 0x62f + 0xcf9) {
        f['push'](parseInt(e[n(0xd7)](g, -0x1 * -0x100a + 0x5ff + -0x1607), -0x6ec + 0x5 * -0x521 + 0x20a1));
    }
    while (f[n(0xc9)] < d) {
        f[n(0xc8)](0x20e7 + -0x8 * -0xb3 + 0x267f * -0x1);
    }
    return f;
}
function modPow(c, d, e) {
    const o = k, f = bytesToBigInt(c), g = bytesToBigInt(d), h = bytesToBigInt(e), i = modPowBI(f, g, h);
    return bigIntToBytes(i, e[o(0xc9)]);
}
let digestInput = [[NODE_COMPUTE_DIGEST_INPUT]], modePowInput = [[NODE_MOD_POW_INPUT]], digestResult, modePowResult;
typeof digestInput === 'undefined' || !digestInput ? digestResult = null : digestResult = computeSHA256([[NODE_COMPUTE_DIGEST_INPUT]]);
if (typeof modePowInput === k(0xcc) || !modePowInput)
    modePowResult = null;
else {
    const {base, exp, mod} = [[NODE_MOD_POW_INPUT]];
    modePowResult = modPow(base, exp, mod);
}
[[NODE_COMPUTE_DIGEST_RESULT]] = digestResult, [[NODE_MOD_POW_RESULT]] = modePowResult;
function a() {
    const p = [
        '982645hpnYcG',
        'crypto',
        '10643jZTaqJ',
        'createHash',
        '391432vECIpc',
        'from',
        '785532gqTLIW',
        '1001756eyAeTr',
        'substr',
        '50wITFgD',
        'toString',
        '6aLemWI',
        'utf8',
        '7MOhdkn',
        'digest',
        'unshift',
        'length',
        '135498ziRaNs',
        'update',
        'undefined',
        'sha256',
        '589545QROdaa'
    ];
    a = function () {
        return p;
    };
    return a();
}
