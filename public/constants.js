"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TELEGRAM_TOKEN = exports.APP_URL = exports.PORT = void 0;
require("dotenv").config();
exports.PORT = Number(process.env.PORT) || 3000;
exports.APP_URL = String(process.env.APP_URL);
exports.TELEGRAM_TOKEN = String(process.env.TELEGRAM_TOKEN);
//# sourceMappingURL=constants.js.map