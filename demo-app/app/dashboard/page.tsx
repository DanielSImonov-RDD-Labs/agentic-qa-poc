import styles from "./dashboard.module.css";

export default function DashboardPage() {
  return (
    <main className={styles.page}>
      <h1 data-testid="welcome-message">Welcome, test@brya.com</h1>
      <p>You have successfully logged in.</p>
    </main>
  );
}
