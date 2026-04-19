#!/bin/bash

# run.sh - سكربت تشغيل البوت الموحد

echo "=========================================="
echo "🚀 Starting RockyTap Unified Bot"
echo "=========================================="

# التأكد من وجود مجلد public
if [ ! -d "public" ]; then
    echo "❌ Error: public folder not found!"
    exit 1
fi

# التأكد من وجود ملف .env
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        echo "❌ Error: .env.example not found!"
        exit 1
    fi
fi

# تشغيل البوت
echo "🤖 Starting bot..."
python3 bot.py