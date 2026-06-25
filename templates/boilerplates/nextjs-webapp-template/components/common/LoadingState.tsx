type LoadingStateProps = {
  message?: string;
};

export function LoadingState({
  message = "Loading data",
}: LoadingStateProps) {
  return (
    <div className="loading-state" role="status">
      <span className="spinner" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}
