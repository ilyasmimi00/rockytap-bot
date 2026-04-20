"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const constants_1 = require("./constants");
const express_1 = __importDefault(require("express"));
const telegraf_1 = require("telegraf");
const bot = new telegraf_1.Telegraf(constants_1.TELEGRAM_TOKEN);
const app = (0, express_1.default)();
app.use(express_1.default.static("static"));
app.use(express_1.default.json());
app.get("/", (_, res) => {
    res.send("Hello World");
});
app.listen(constants_1.PORT, () => {
    console.log(`Server is Fire at http://localhost:${constants_1.PORT}`);
});
bot.command("start", (ctx) => {
    return ctx.reply(`Play Cool Frog!`, {
        reply_markup: {
            inline_keyboard: [
                [
                    {
                        text: `Play Game`,
                        web_app: { url: `${constants_1.APP_URL}/` },
                    },
                ],
            ],
        },
    });
});
bot.launch();
exports.default = app;
//# sourceMappingURL=index.js.map