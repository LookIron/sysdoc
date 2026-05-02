CREATE TABLE IF NOT EXISTS pending_commands (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  machine_id   UUID REFERENCES machines(id) ON DELETE CASCADE,
  fix_code     TEXT NOT NULL,
  params       JSONB DEFAULT '{}',
  status       TEXT DEFAULT 'queued' CHECK (status IN ('queued','running','success','failed')),
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  output       TEXT,
  success      BOOLEAN
);
