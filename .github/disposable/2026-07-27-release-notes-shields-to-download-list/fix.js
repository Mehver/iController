import {Octokit} from "@octokit/rest";

const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
});

const [owner, repo] = process.env.GITHUB_REPOSITORY.split("/");

const DRY_RUN = process.env.DRY_RUN === "true";

// 单个 shields 下载按钮: [![](<img.shields.io badge url>)](<download url>)
const BADGE_RE = /\[!\[\]\((https:\/\/img\.shields\.io\/badge\/.+?)\)\]\((https:\/\/[^\s)]+)\)/g;

// 正文开头连续的按钮块（按钮之间允许任意空白）
const LEADING_BLOCK_RE = /^(?:\[!\[\]\(https:\/\/img\.shields\.io\/badge\/.+?\)\]\(https:\/\/[^\s)]+\)\s*)+/;

// 从 badge 图片 URL 中解析出可读文本，例如
// /badge/Windows%20(x64)%20CLI-v0.7.2-blue → "Windows (x64) CLI v0.7.2"
function badgeText(imgUrl, linkUrl) {
    try {
        const path = new URL(imgUrl).pathname;
        const raw = decodeURIComponent(path.replace(/^\/badge\//, ""));
        const parts = raw.split("-");
        if (parts.length >= 3) {
            const message = parts[parts.length - 2];
            const label = parts.slice(0, parts.length - 2).join("-");
            return `${label} ${message}`.trim();
        }
    } catch {
        // 解析失败则走兜底
    }
    return linkUrl.split("/").pop();
}

// 把开头的 shields 按钮块替换为 "### Download" + 无序列表，失败时返回 null
function transform(body) {
    const blockMatch = body.match(LEADING_BLOCK_RE);
    if (!blockMatch) {
        return null;
    }

    const block = blockMatch[0];
    const badges = [...block.matchAll(BADGE_RE)];
    if (badges.length === 0) {
        return null;
    }

    const items = badges.map(
        ([, imgUrl, linkUrl]) => `- [${badgeText(imgUrl, linkUrl)}](${linkUrl})`
    );

    const rest = body.slice(block.length).replace(/^\s+/, "");

    return {
        updatedBody: `### Download\n\n${items.join("\n")}\n\n${rest}`,
        items,
    };
}

async function run() {
    const releases = await octokit.paginate(
        octokit.repos.listReleases,
        {owner, repo, per_page: 100}
    );

    for (const release of releases) {
        if (!release.body) {
            continue;
        }

        const result = transform(release.body);
        if (!result || result.updatedBody === release.body) {
            continue;
        }

        console.log(`→ ${release.tag_name}`);
        for (const item of result.items) {
            console.log(`  ${item}`);
        }

        if (DRY_RUN) {
            console.log("  DRY-RUN: would update");
            continue;
        }

        await octokit.repos.updateRelease({
            owner,
            repo,
            release_id: release.id,
            body: result.updatedBody,
        });

        console.log("  updated");
    }
}

run().catch(err => {
    console.error(err);
    process.exit(1);
});
