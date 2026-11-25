-- Добавление управляемого состояния QR-сессии для лабораторной работы №7.
ALTER TABLE qr_sessions
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active',
    ADD COLUMN closed_at TIMESTAMPTZ;

ALTER TABLE qr_sessions
    ADD CONSTRAINT chk_qr_sessions_status CHECK (status IN ('active', 'closed', 'cancelled', 'expired'));

CREATE INDEX idx_qr_sessions_lesson_status ON qr_sessions(lesson_id, status);

-- Гарантирует единственную активную QR-сессию для занятия даже при параллельных запросах.
CREATE UNIQUE INDEX uq_qr_sessions_one_active_per_lesson ON qr_sessions(lesson_id) WHERE status = 'active';
