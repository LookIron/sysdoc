-- SysDoc initial schema

CREATE TABLE IF NOT EXISTS machines (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  machine_id   TEXT UNIQUE NOT NULL,
  hostname     TEXT,
  os_name      TEXT,
  os_arch      TEXT,
  cpu_model    TEXT,
  cpu_cores    INT,
  ram_total_gb FLOAT,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  last_seen    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS scans (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  machine_id        UUID REFERENCES machines(id) ON DELETE CASCADE,
  scanned_at        TIMESTAMPTZ DEFAULT NOW(),
  health_score      INT,
  score_performance INT,
  score_storage     INT,
  score_security    INT,
  score_stability   INT,
  raw_data          JSONB
);

CREATE TABLE IF NOT EXISTS issues (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id       UUID REFERENCES scans(id) ON DELETE CASCADE,
  machine_id    UUID REFERENCES machines(id) ON DELETE CASCADE,
  issue_code    TEXT NOT NULL,
  severity      TEXT NOT NULL CHECK (severity IN ('critical','high','medium','low')),
  title         TEXT NOT NULL,
  description   TEXT,
  fix_available BOOLEAN DEFAULT FALSE,
  fix_command   TEXT,
  resolved_at   TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS metrics (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  machine_id       UUID REFERENCES machines(id) ON DELETE CASCADE,
  recorded_at      TIMESTAMPTZ DEFAULT NOW(),
  cpu_usage_pct    FLOAT,
  cpu_temp_c       FLOAT,
  cpu_freq_mhz     FLOAT,
  cpu_freq_max_mhz FLOAT,
  ram_usage_pct    FLOAT,
  ram_available_gb FLOAT,
  disk_read_mbps   FLOAT,
  disk_write_mbps  FLOAT,
  disk_usage_pct   FLOAT,
  net_upload_mbps  FLOAT,
  net_download_mbps FLOAT
);

CREATE TABLE IF NOT EXISTS fix_history (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  machine_id UUID REFERENCES machines(id) ON DELETE CASCADE,
  issue_id   UUID REFERENCES issues(id),
  fix_code   TEXT,
  applied_at TIMESTAMPTZ DEFAULT NOW(),
  success    BOOLEAN,
  output     TEXT
);
