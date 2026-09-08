# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import posixpath
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

JS_DOM_DEEP_INSPECTOR = r"""
(() => {
    "use strict";
    const output = {
        blocks: [],
        rawLastMessage: "",
        meta: {
            scopeSelector: "",
            selectorUsed: "",
            codeBlockCount: 0,
            shadowRootsVisited: 0,
            iframesVisited: 0
        }
    };

    const safeText = (el) => {
        if (!el) return "";
        try {
            const text = typeof el.innerText === "string" ? el.innerText : (el.textContent || "");
            return String(text).replace(/\u00a0/g, " ").replace(/\r\n?/g, "\n").trim();
        } catch (_) {
            return "";
        }
    };

    const safeAttr = (el, name) => {
        try {
            return el && el.getAttribute ? (el.getAttribute(name) || "") : "";
        } catch (_) {
            return "";
        }
    };

    const deepQuerySelectorAll = (selector, root = document) => {
        const results = [];
        const visitedRoots = new Set();
        const visitedDocuments = new Set();

        const visitRoot = (currentRoot) => {
            if (!currentRoot || visitedRoots.has(currentRoot)) return;
            visitedRoots.add(currentRoot);
            try {
                currentRoot.querySelectorAll(selector).forEach((el) => {
                    if (!results.includes(el)) results.push(el);
                });
            } catch (_) {}

            let all = [];
            try {
                all = Array.from(currentRoot.querySelectorAll("*"));
            } catch (_) {}

            for (const el of all) {
                try {
                    if (el.shadowRoot) {
                        output.meta.shadowRootsVisited += 1;
                        visitRoot(el.shadowRoot);
                    }
                } catch (_) {}

                if (el.tagName === "IFRAME") {
                    try {
                        const doc = el.contentDocument;
                        if (doc && !visitedDocuments.has(doc)) {
                            visitedDocuments.add(doc);
                            output.meta.iframesVisited += 1;
                            visitRoot(doc);
                        }
                    } catch (_) {}
                }
            }
        };
        visitRoot(root);
        return results;
    };

    const responseSelectors = [
        '[data-message-author-role="model"]',
        '[data-testid="conversation-turn-model"]',
        'message-content',
        '.model-response-text',
        '.response-container',
        '.presented-content',
        '.chat-message-content',
        'div.markdown'
    ];

    let targetScope = null;
    let selectorUsed = "";

    for (const selector of responseSelectors) {
        const nodes = deepQuerySelectorAll(selector);
        if (nodes.length > 0) {
            targetScope = nodes[nodes.length - 1];
            selectorUsed = selector;
            break;
        }
    }

    if (!targetScope) {
        targetScope = document.body;
        selectorUsed = "document.body";
    }

    output.meta.selectorUsed = selectorUsed;
    output.rawLastMessage = safeText(targetScope);

    const codeSelectors = [
        "code-block",
        "pre",
        ".code-container",
        "div[class*='code-block']",
        "[data-code-block]",
        "pre code"
    ];

    const codeHolders = [];
    const seenHolders = new Set();

    for (const selector of codeSelectors) {
        const nodes = deepQuerySelectorAll(selector, targetScope);
        for (const node of nodes) {
            if (!seenHolders.has(node)) {
                seenHolders.add(node);
                codeHolders.push(node);
            }
        }
        if (codeHolders.length > 0 && selector === "code-block") continue;
    }

    const findHeader = (holder, codeElement) => {
        const candidates = [
            ".header", ".code-header", ".toolbar", ".file-name",
            "[class*='file-name']", "[class*='language']", "[class*='header']",
            "button[aria-label]", "span[class*='label']"
        ];
        for (const selector of candidates) {
            try {
                const node = holder.querySelector(selector);
                if (node) {
                    const txt = safeText(node);
                    if (txt && txt.length <= 250) return txt;
                    const aria = safeAttr(node, "aria-label");
                    if (aria && aria.length <= 250) return aria.trim();
                }
            } catch (_) {}
        }
        const attrs = ["data-filename", "data-file-name", "data-language", "filename", "language"];
        for (const attr of attrs) {
            const value = safeAttr(holder, attr);
            if (value) return value.trim();
        }
        return "";
    };

    const findLanguage = (holder, codeElement) => {
        const attrs = ["language", "data-language", "data-lang"];
        for (const attr of attrs) {
            const value = safeAttr(holder, attr);
            if (value) return value.trim().toLowerCase();
        }
        if (codeElement) {
            for (const attr of attrs) {
                const value = safeAttr(codeElement, attr);
                if (value) return value.trim().toLowerCase();
            }
            const className = String(codeElement.className || "");
            const match = className.match(/(?:language|lang)-([a-zA-Z0-9_+\-.]+)/);
            if (match) return match[1].toLowerCase();
        }
        return "";
    };

    const previousText = (holder) => {
        let node = holder.previousElementSibling;
        let depth = 0;
        while (node && depth < 5) {
            const text = safeText(node);
            if (text && text.length <= 300) return text;
            node = node.previousElementSibling;
            depth++;
        }
        return "";
    };

    for (let index = 0; index < codeHolders.length; index++) {
        const holder = codeHolders[index];
        try {
            const codeElement = holder.matches && holder.matches("code") ? holder : (holder.querySelector("code") || holder);
            const codeText = safeText(codeElement);
            if (!codeText || codeText.length < 2) continue;
            output.blocks.push({
                id: index + 1,
                header: findHeader(holder, codeElement),
                lang: findLanguage(holder, codeElement),
                prevText: previousText(holder),
                code: codeText,
                elementTag: holder.tagName || "",
                dataLanguage: safeAttr(holder, "data-language"),
                dataFilename: safeAttr(holder, "data-filename")
            });
        } catch (_) {}
    }
    output.meta.codeBlockCount = output.blocks.length;
    return JSON.stringify(output);
})();
"""

@dataclass
class ExtractedFile:
    target: str
    code: str
    confidence: float
    reason: str
    size: int = field(init=False)

    def __post_init__(self) -> None:
        self.target = CodeIntelligenceExtractor.normalize_filename(self.target)
        self.code = CodeIntelligenceExtractor.clean_code(self.code)
        self.confidence = max(0.0, min(1.0, float(self.confidence)))
        self.size = len(self.code.encode("utf-8"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "code": self.code,
            "confidence": round(self.confidence, 4),
            "reason": self.reason,
            "size": self.size,
        }

class CodeIntelligenceExtractor:
    RE_TAG_BLOCK = re.compile(
        r"<<<FILE:\s*(?P<filename>[^\n>]+?)\s*>>>\s*(?P<code>[\s\S]*?)<<<END_FILE>>>",
        re.IGNORECASE
    )
    RE_MARKDOWN_CODE = re.compile(
        r"(?:```(?P<lang1>[a-zA-Z0-9_+.\-]*)[ \t]*\r?\n(?P<code1>[\s\S]*?)```|~~~(?P<lang2>[a-zA-Z0-9_+.\-]*)[ \t]*\r?\n(?P<code2>[\s\S]*?)~~~)",
        re.IGNORECASE
    )
    RE_FILE_PATH = re.compile(r"(?:[a-zA-Z0-9_\-]+/)*[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]{1,16}")
    RE_EXPLICIT_PATH_LINE = re.compile(rf"(?:filepath|filename|file|path|dosya)\s*(?:[:=]|->)\s*[`'\" ]*(?P<path>{RE_FILE_PATH.pattern})", re.IGNORECASE)
    RE_COMMENT_PATH_LINE = re.compile(rf"^\s*(?://|\#|/\*|<!--)\s*[`'\" ]*(?P<path>{RE_FILE_PATH.pattern})", re.IGNORECASE)
    RE_INLINE_PATH = re.compile(rf"`(?P<path>(?:[a-zA-Z0-9_\-]+/)*[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]{{1,16}})`")

    LANGUAGE_ALIASES = {
        "js": "javascript", "jsx": "javascript", "ts": "typescript", "tsx": "typescript",
        "py": "python", "rb": "ruby", "sh": "shell", "bash": "shell", "zsh": "shell",
        "yml": "yaml", "md": "markdown", "htm": "html",
    }

    EXTENSION_TO_LANGUAGE = {
        "js": "javascript", "jsx": "javascript", "ts": "typescript", "tsx": "typescript",
        "py": "python", "php": "php", "java": "java", "go": "go", "rs": "rust",
        "css": "css", "scss": "scss", "html": "html", "json": "json", "yaml": "yaml",
        "yml": "yaml", "sql": "sql", "sh": "shell"
    }

    @classmethod
    def clean_code(cls, raw: str) -> str:
        if not raw: return ""
        text = str(raw).replace("\r\n", "\n").replace("\r", "\n")
        lines = text.splitlines()
        if lines and lines[0].strip().startswith(("```", "~~~")): lines = lines[1:]
        if lines and lines[-1].strip() in ("```", "~~~"): lines = lines[:-1]
        return "\n".join(line.rstrip() for line in lines).strip()

    @classmethod
    def normalize_filename(cls, path_str: str) -> str:
        if not path_str: return "script.js"
        clean = str(path_str).strip("`'\"* ").replace("\\", "/")
        clean = re.sub(r"\s+", " ", clean)
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", clean): return "script.js"
        clean = re.sub(r"^[a-zA-Z]:[/\\]+", "", clean).lstrip("/")
        parts = []
        for part in clean.split("/"):
            part = part.strip().replace("\x00", "")
            part = re.sub(r'[<>:"|?*]', "_", part)
            part = re.sub(r"[\x00-\x1f]", "", part)
            if not part or part == ".": continue
            if part == "..":
                if parts: parts.pop()
                continue
            parts.append(part)
        normalized = posixpath.normpath("/".join(parts)).lstrip("./") if parts else "script.js"
        return normalized or "script.js"

    @classmethod
    def _language_normalize(cls, lang: str) -> str:
        value = (lang or "").strip().lower()
        return cls.LANGUAGE_ALIASES.get(value, value)

    @classmethod
    def _looks_like_filename(cls, value: str) -> bool:
        if not value or len(value.strip()) > 220: return False
        return bool(cls.RE_FILE_PATH.search(value))

    @classmethod
    def _guess_by_syntax(cls, code: str, lang: str = "") -> str:
        sample = cls.clean_code(code[:2500]).lower()
        language = cls._language_normalize(lang)

        if language == "json" or sample.strip().startswith("{"):
            if '"dependencies"' in sample or '"devdependencies"' in sample: return "package.json"
            if '"compileroptions"' in sample: return "tsconfig.json"
            return "config.json"
        if language == "yaml" or "services:" in sample:
            if "services:" in sample and "version:" in sample: return "docker-compose.yml"
            return "config.yml"
        if re.search(r"<!doctype\s+html", sample) or re.search(r"<html[\s>]", sample): return "index.html"
        if language in {"css", "scss", "sass"} or re.search(r"[.#]?[a-zA-Z_-][\w-]*\s*\{", sample):
            return "style.scss" if language == "scss" else "style.css"
        if "import react" in sample or "from 'react'" in sample:
            return "App.tsx" if language == "typescript" else "App.jsx"
        if language == "typescript": return "main.ts"
        if language == "javascript": return "script.js"
        if re.search(r"^\s*def\s+\w+\(", sample, re.MULTILINE) or language == "python": return "main.py"
        if re.search(r"\bselect\b", sample) and re.search(r"\bfrom\b", sample): return "query.sql"
        if language == "dockerfile" or re.search(r"^\s*FROM\s+\S+", sample, re.MULTILINE): return "Dockerfile"
        if "<?php" in sample or language == "php": return "index.php"
        if language == "java" or re.search(r"\bpublic\s+class\s+\w+", sample): return "Main.java"
        if language == "go" or re.search(r"\bpackage\s+main\b", sample): return "main.go"
        if language == "rust" or "fn main()" in sample: return "main.rs"
        if language == "shell" or sample.startswith("#!/bin/"): return "script.sh"
        
        return "script.js"

    @classmethod
    def _resolve_target(cls, block_info: Dict[str, Any], context_text: str) -> Tuple[str, float, str]:
        code = str(block_info.get("code") or "")
        header = str(block_info.get("header") or "")
        prev_text = str(block_info.get("prevText") or "")
        lang = str(block_info.get("lang") or "")
        data_filename = str(block_info.get("dataFilename") or "").strip()

        if cls._looks_like_filename(data_filename):
            match = cls.RE_FILE_PATH.search(data_filename)
            if match: return cls.normalize_filename(match.group(0)), 0.995, "DOM data-filename özniteliği"

        for line in code.splitlines()[:8]:
            explicit = cls.RE_EXPLICIT_PATH_LINE.search(line)
            if explicit: return cls.normalize_filename(explicit.group("path")), 0.99, "Kod Başı Direktifi"
            comment = cls.RE_COMMENT_PATH_LINE.search(line)
            if comment: return cls.normalize_filename(comment.group("path")), 0.94, "Satır Başı Yorum Başlığı"

        if cls._looks_like_filename(header):
            match = cls.RE_FILE_PATH.search(header)
            if match: return cls.normalize_filename(match.group(0)), 0.91, "DOM Kod Blok Başlığı"

        if cls._looks_like_filename(prev_text):
            match = cls.RE_FILE_PATH.search(prev_text)
            if match: return cls.normalize_filename(match.group(0)), 0.86, "Kod Bloğu Öncesindeki Başlık/Paragraf"

        if context_text and code:
            position = context_text.find(code[:100])
            if position >= 0:
                left = context_text[max(0, position - 500):position]
                matches = list(cls.RE_INLINE_PATH.finditer(left))
                if matches: return cls.normalize_filename(matches[-1].group("path")), 0.82, "Yakın Metin İçindeki Inline Dosya Adı"

        filename = cls._guess_by_syntax(code, lang)
        return filename, (0.48 if lang else 0.40), ("Dil Etiketi + İçerik Sentaks Sezgisi" if lang else "İçerik Sentaks Sezgisi")

    @classmethod
    def parse_payload(cls, payload: Dict[str, Any], *, deduplicate: bool = True) -> List[ExtractedFile]:
        if not isinstance(payload, dict): return []
        raw_text = payload.get("rawLastMessage", "")
        blocks = payload.get("blocks", [])
        extracted = []

        for match in cls.RE_TAG_BLOCK.finditer(raw_text or ""):
            code = cls.clean_code(match.group("code"))
            if code:
                extracted.append(ExtractedFile(target=match.group("filename").strip(), code=code, confidence=1.0, reason="Özel Format Direktifi (<<<FILE>>>)"))

        if extracted: return cls._deduplicate_files(extracted) if deduplicate else extracted

        for block in blocks:
            if not isinstance(block, dict): continue
            code = cls.clean_code(block.get("code", ""))
            if len(code) < 2: continue
            target, confidence, reason = cls._resolve_target(block, raw_text)
            extracted.append(ExtractedFile(target=target, code=code, confidence=confidence, reason=reason))

        if not extracted and raw_text:
            for match in cls.RE_MARKDOWN_CODE.finditer(raw_text):
                lang = match.group("lang1") or match.group("lang2") or ""
                code = cls.clean_code(match.group("code1") if match.group("code1") is not None else match.group("code2"))
                if code:
                    target = cls._guess_by_syntax(code, lang)
                    extracted.append(ExtractedFile(target=target, code=code, confidence=0.58 if lang else 0.45, reason=f"Markdown Code Fence ({lang or 'düz'})"))

        return cls._deduplicate_files(extracted) if deduplicate else extracted

    @classmethod
    def _deduplicate_files(cls, files: Sequence[ExtractedFile]) -> List[ExtractedFile]:
        best_by_target = {}
        exact_seen = set()
        for item in files:
            exact_key = (item.target, item.code)
            if exact_key in exact_seen: continue
            exact_seen.add(exact_key)
            previous = best_by_target.get(item.target)
            if previous is None or item.confidence > previous.confidence:
                best_by_target[item.target] = item
        return list(best_by_target.values())

if __name__ == "__main__":
    pass