import { formatDateTime } from "@/lib/format";
import type { AppEvent } from "@/lib/types";

type EventListProps = {
  events: AppEvent[];
};

const levelClassName: Record<AppEvent["level"], string> = {
  INFO: "level-info",
  WARN: "level-warn",
  ERROR: "level-error",
};

export function EventList({ events }: EventListProps) {
  return (
    <div className="event-list">
      {events.map((event) => (
        <article className="event-item" key={`${event.timestamp}-${event.message}`}>
          <div className="event-row">
            <span className="event-source">{event.source}</span>
            <span className={`level-badge ${levelClassName[event.level]}`}>
              {event.level}
            </span>
          </div>
          <p className="event-message">{event.message}</p>
          <time className="event-time" dateTime={event.timestamp}>
            {formatDateTime(event.timestamp)}
          </time>
        </article>
      ))}
    </div>
  );
}
