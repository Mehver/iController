import {Octokit} from "@octokit/rest";

const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
});

const owner = process.env.GITHUB_REPOSITORY.split("/")[0];
const repo = process.env.GITHUB_REPOSITORY.split("/")[1];

const DRY_RUN = process.env.DRY_RUN === "true";

const FROM = "?logo=Windows";
const TO =
    "?logo=data:image/svg+xml;base64,PHN2ZyBoZWlnaHQ9IjI1MDAiIHByZXNlcnZlQXNwZWN0UmF0aW89InhNaWRZTWlkIiB3aWR0aD0iMjQ5MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB2aWV3Qm94PSItMSAtMSAyNTggMjU5Ij48cGF0aCBkPSJNLTEtMWgyNTh2MjU5SC0xeiIvPjxwYXRoIGQ9Ik0wIDM2LjM1N0wxMDQuNjIgMjIuMTFsLjA0NSAxMDAuOTE0LTEwNC41Ny41OTVMMCAzNi4zNTh2LS4wMDF6bTEwNC41NyA5OC4yOTNsLjA4IDEwMS4wMDJMLjA4MSAyMjEuMjc1bC0uMDA2LTg3LjMwMiAxMDQuNDk0LjY3N3ptMTIuNjgyLTExNC40MDVMMjU1Ljk2OCAwdjEyMS43NGwtMTM4LjcxNiAxLjFWMjAuMjQ2ek0yNTYgMTM1LjZsLS4wMzMgMTIxLjE5MS0xMzguNzE2LTE5LjU3OC0uMTk0LTEwMS44NHoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=";

async function run() {
    const releases = await octokit.paginate(
        octokit.repos.listReleases,
        {owner, repo, per_page: 100}
    );

    for (const r of releases) {
        if (!r.body || !r.body.includes(FROM)) {
            continue;
        }

        const updated = r.body.replaceAll(FROM, TO);

        if (updated === r.body) {
            continue;
        }

        console.log(`→ ${r.tag_name}`);

        if (DRY_RUN) {
            console.log("  DRY-RUN: would update");
            continue;
        }

        await octokit.repos.updateRelease({
            owner,
            repo,
            release_id: r.id,
            body: updated,
        });

        console.log("  updated");
    }
}

run().catch(err => {
    console.error(err);
    process.exit(1);
});
