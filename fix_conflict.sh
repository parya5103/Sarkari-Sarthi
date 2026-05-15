#!/bin/bash
git checkout --ours script.js
git checkout --ours style.css
git add script.js style.css
git rebase --continue
