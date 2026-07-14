type ErrorStateProps = {
  title?: string;
  message: string;
};

export function ErrorState({
  title = "Unable to load data",
  message,
}: ErrorStateProps) {
  return (
    <div className="error-state" role="alert">
      <strong>{title}</strong>
      <span>{message}</span>
    </div>
  );
}
