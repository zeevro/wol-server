#!/bin/sh
for s in 32 48 72 96 128 256; do
  ffmpeg -y -i icon.svg -s ${s}x${s} icon-$s.png
done

echo "  \"icons\": ["
for s in 32 48 72 96 128 256; do
  echo "    {"
  echo "      \"src\": \"icon-$s.png\","
  echo "      \"sizes\": \"${s}x${s}\""
  echo "    },"
done
echo "    {"
echo "      \"src\": \"icon.svg\","
echo "      \"sizes\": \"any\""
echo "    }"
echo "  ]"
