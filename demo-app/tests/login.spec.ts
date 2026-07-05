import { test, expect } from "@playwright/test";

test("logs in successfully with valid credentials", async ({ page }) => {
  await page.goto("/login");

  await page.getByTestId("email-input").fill("test@brya.com");
  await page.getByTestId("password-input").fill("123456");
  await page.getByTestId("login-submit").click();

  await expect(page).toHaveURL("/dashboard");
  await expect(page.getByTestId("welcome-message")).toHaveText(
    "Welcome, test@brya.com"
  );
});
