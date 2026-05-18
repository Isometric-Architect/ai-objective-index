const BASE_URL = "http://127.0.0.1:8000";

async function getJson(path) {
  try {
    const response = await fetch(`${BASE_URL}${path}`);
    return await response.json();
  } catch (error) {
    console.log("AOI API is not running. Start it with: python -m ai_objective_index.api");
    return null;
  }
}

async function main() {
  const search = await getJson("/search?query=cheap%20image%20generation%20API&limit=3&data_scope=sample");
  if (!search || !search.results || search.results.length === 0) return;

  console.log(JSON.stringify(search, null, 2));
  const integrated = await getJson("/search?query=cheap%20image%20generation%20API&limit=3&data_scope=integrated");
  if (integrated) console.log(JSON.stringify({ integrated_example: integrated }, null, 2));
  const curated = await getJson("/search?query=cheap%20image%20generation%20API&limit=3&data_scope=curated");
  if (curated) console.log(JSON.stringify({ curated_example: curated }, null, 2));
  const publicBeta = await getJson("/search?query=cheap%20image%20generation%20API&limit=3&data_scope=public_beta");
  if (publicBeta) console.log(JSON.stringify({ public_beta_example: publicBeta }, null, 2));
  const mcpRegistry = await getJson("/search?query=browser%20automation%20MCP&limit=3&data_scope=mcp_registry");
  if (mcpRegistry) console.log(JSON.stringify({ mcp_registry_example: mcpRegistry }, null, 2));
  const publicBetaMcp = await getJson("/search?query=browser%20automation%20MCP&limit=3&data_scope=public_beta_mcp");
  if (publicBetaMcp) {
    console.log(JSON.stringify({
      public_beta_mcp_example: publicBetaMcp,
      note: "public_beta_mcp rows are registry metadata candidates, not verified or security certified; it may be empty in fixture mode."
    }, null, 2));
  }

  const objectId = search.results[0].object_id;
  const score = await getJson(`/objects/${objectId}/score?data_scope=sample`);
  if (score) console.log(JSON.stringify(score, null, 2));
}

main();
