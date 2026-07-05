"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import styles from "./login.module.css";

const VALID_EMAIL = "test@brya.com";
const VALID_PASSWORD = "123456";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (email === VALID_EMAIL && password === VALID_PASSWORD) {
      setError("");
      router.push("/dashboard");
      return;
    }

    setError("Invalid email or password.");
  }

  return (
    <main className={styles.page}>
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        <h1>Sign in</h1>

        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          data-testid="email-input"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          data-testid="password-input"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        <button type="submit" data-testid="login-submit">
          Log in
        </button>

        {error && (
          <p role="alert" data-testid="login-error" className={styles.error}>
            {error}
          </p>
        )}
      </form>
    </main>
  );
}
