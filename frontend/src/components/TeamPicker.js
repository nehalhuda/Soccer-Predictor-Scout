import { useEffect, useState } from "react";

export default function TeamPicker() {
  const [teams, setTeams] = useState([]);
  const [home, setHome] = useState("");
  const [away, setAway] = useState("");
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    fetch("/api/teams_fd?competition=PL")
      .then(r => r.json())
      .then(setTeams)
      .catch(console.error);
  }, []);

  const predict = async () => {
    const r = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ home_team: home, away_team: away })
    });
    setPrediction(await r.json());
  };

  return (
    <div style={{ maxWidth: 720, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h2>Premier League Teams</h2>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 16 }}>
        {teams.map(t => (
          <div key={t.id} style={{ border: "1px solid #eee", borderRadius: 12, padding: 12, textAlign: "center" }}>
            <img src={t.crest} alt={t.name} style={{ height: 48, objectFit: "contain" }} />
            <div style={{ marginTop: 8, fontSize: 14 }}>{t.name}</div>
          </div>
        ))}
      </div>

      <h3 style={{ marginTop: 24 }}>Predict</h3>
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <select value={home} onChange={e => setHome(e.target.value)}>
          <option value="">Home team…</option>
          {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
        <span>vs</span>
        <select value={away} onChange={e => setAway(e.target.value)}>
          <option value="">Away team…</option>
          {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
        <button disabled={!home || !away} onClick={predict}>Predict</button>
      </div>

      {prediction && (
        <pre style={{ background: "#f7f7f7", padding: 12, borderRadius: 8, marginTop: 16 }}>
{JSON.stringify(prediction, null, 2)}
        </pre>
      )}
    </div>
  );
  useEffect(() => {
    console.log("Fetching teams…");
    fetch("/api/teams_fd?competition=PL")
      .then(r => {
        console.log("Status:", r.status);
        return r.json();
      })
      .then(data => {
        console.log("Teams:", data);
        setTeams(data);
      })
      .catch(err => console.error("Fetch error:", err));
  }, []);



}
