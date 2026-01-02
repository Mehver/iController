import {Octokit} from "@octokit/rest";

const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
});

const [owner, repo] = process.env.GITHUB_REPOSITORY.split("/");

const DRY_RUN = process.env.DRY_RUN === "true";

const FROM_HEADING = "### What's Changed";
const TO_HEADING = "### Bot Updates";

async function run() {
    const releases = await octokit.paginate(
        octokit.repos.listReleases,
        {owner, repo, per_page: 100}
    );

    for (const release of releases) {
        if (!release.body || !release.body.includes(FROM_HEADING)) {
            continue;
        }

        const updatedBody = release.body.replaceAll(FROM_HEADING, TO_HEADING);

        if (updatedBody === release.body) {
            // 理论上不会走到这里，但保险起见
            continue;
        }

        console.log(`→ ${release.tag_name}`);
        console.log(`  replacing "${FROM_HEADING}" → "${TO_HEADING}"`);

        if (DRY_RUN) {
            console.log("  DRY-RUN: would update");
            continue;
        }

        await octokit.repos.updateRelease({
            owner,
            repo,
            release_id: release.id,
            body: updatedBody,
        });

        console.log("  updated");
    }
}

run().catch(err => {
    console.error(err);
    process.exit(1);
});
