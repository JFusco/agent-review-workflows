"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { git, today } = require("./common.cjs");

function isoDateFromMs(ms) {
  return new Date(ms).toISOString().slice(0, 10);
}

function validDate(value) {
  return typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value);
}

function dateFromPlanBasename(sourcePath) {
  if (!sourcePath) return "";
  const base = path.basename(String(sourcePath), ".md").replace(/\.plan$/, "");
  const dated = base.match(/^(\d{4}-\d{2}-\d{2})-(.+)$/);
  return dated ? dated[1] : "";
}

function dateFromSessionPath(sourcePath) {
  const match = String(sourcePath).match(/\/(\d{4})\/(\d{2})\/(\d{2})\//);
  return match ? `${match[1]}-${match[2]}-${match[3]}` : "";
}

function gitCommitDate(root, hash) {
  if (!hash) return "";
  const out = git(["log", "-1", "--format=%cI", hash], root);
  return out ? out.slice(0, 10) : "";
}

function fileMtimeDate(file) {
  try {
    if (!file || !fs.existsSync(file)) return "";
    return isoDateFromMs(fs.statSync(file).mtimeMs);
  } catch {
    return "";
  }
}

function evidenceDates(root, evidence = []) {
  const dates = [];
  for (const line of evidence || []) {
    const merge = String(line).match(/merge ([0-9a-f]{7,40})/i);
    if (merge) {
      const date = gitCommitDate(root, merge[1]);
      if (date) dates.push(date);
    }
    const commit = String(line).match(/^commit ([0-9a-f]{7,40})\b/i);
    if (commit) {
      const date = gitCommitDate(root, commit[1]);
      if (date) dates.push(date);
    }
  }
  return dates;
}

function sourcePathDates(root, candidate) {
  const dates = [];
  for (const item of candidate?.sources || []) {
    const source = String(item?.source || "");
    const fromName = dateFromPlanBasename(source);
    if (fromName) dates.push(fromName);
    const fromSession = dateFromSessionPath(source);
    if (fromSession) dates.push(fromSession);
    const gitSource = source.match(/^git:([0-9a-f]+):/i);
    if (gitSource) {
      const date = gitCommitDate(root, gitSource[1]);
      if (date) dates.push(date);
      continue;
    }
    const resolved = path.isAbsolute(source) ? source : path.join(root, source);
    const date = fileMtimeDate(resolved);
    if (date) dates.push(date);
  }
  return dates;
}

function inferPlanDate(root, candidate, evidence = [], status = "") {
  for (const item of candidate?.sources || []) {
    const fromName = dateFromPlanBasename(item?.source);
    if (validDate(fromName)) return fromName;
    const fromSession = dateFromSessionPath(item?.source);
    if (validDate(fromSession)) return fromSession;
  }
  const delivery = evidenceDates(root, evidence);
  if (["implemented", "partial"].includes(status) && delivery.length) {
    return delivery.sort().pop();
  }
  const authored = sourcePathDates(root, candidate);
  if (authored.length) return authored.sort()[0];
  if (delivery.length) return delivery.sort().pop();
  return today();
}

module.exports = {
  inferPlanDate,
  dateFromPlanBasename,
  dateFromSessionPath,
  gitCommitDate,
  fileMtimeDate,
  evidenceDates,
  sourcePathDates,
};
