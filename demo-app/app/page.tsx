import Link from "next/link";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <div className={styles.intro}>
          <h1>Agentic QA Demo App</h1>
          <p>A minimal target application for exercising QA automation.</p>
        </div>
        <div className={styles.ctas}>
          <Link className={styles.primary} href="/login">
            Go to Login
          </Link>
        </div>
      </main>
    </div>
  );
}
