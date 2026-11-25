DROP INDEX IF EXISTS uq_qr_sessions_one_active_per_lesson;
DROP INDEX IF EXISTS idx_qr_sessions_lesson_status;
ALTER TABLE qr_sessions DROP CONSTRAINT IF EXISTS chk_qr_sessions_status;
ALTER TABLE qr_sessions DROP COLUMN IF EXISTS closed_at;
ALTER TABLE qr_sessions DROP COLUMN IF EXISTS status;
