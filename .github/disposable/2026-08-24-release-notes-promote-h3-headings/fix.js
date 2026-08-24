import {Octokit} from "@octokit/rest";

const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
});

const [owner, repo] = process.env.GITHUB_REPOSITORY.split("/");

const DRY_RUN = process.env.DRY_RUN === "true";

function promoteHeadings(body) {
    let fence;
    let count = 0;
    const parts = body.split(/(\r?\n)/);

    for (let index = 0; index < parts.length; index += 2) {
        const line = parts[index];

        if (fence) {
            const closingFence = new RegExp(
                `^[ \\t]{0,3}${fence.character}{${fence.length},}[ \\t]*$`
            );
            if (closingFence.test(line)) {
                fence = undefined;
            }
            continue;
        }

        const openingFence = line.match(/^[ \t]{0,3}(`{3,}|~{3,})/);
        if (openingFence) {
            fence = {
                character: openingFence[1][0],
                length: openingFence[1].length,
            };
            continue;
        }

        if (/^[ \t]{0,3}###(?!#)(?=[ \t]|$)/.test(line)) {
            parts[index] = line.replace(/^([ \t]{0,3})###/, "$1##");
            count += 1;
        }
    }

    return {body: parts.join(""), count};
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

        const result = promoteHeadings(release.body);
        if (result.count === 0) {
            continue;
        }

        console.log(`→ ${release.tag_name}`);
        console.log(`  promoting ${result.count} level-three heading(s)`);

        if (DRY_RUN) {
            console.log("  DRY-RUN: would update");
            continue;
        }

        await octokit.repos.updateRelease({
            owner,
            repo,
            release_id: release.id,
            body: result.body,
        });

        console.log("  updated");
    }
}

run().catch(err => {
    console.error(err);
    process.exit(1);
});
