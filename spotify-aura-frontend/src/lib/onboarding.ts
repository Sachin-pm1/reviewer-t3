const ONBOARDING_KEY = "spotify-aura-onboarding-complete";

export function isOnboardingComplete(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(ONBOARDING_KEY) === "true";
}

export function setOnboardingComplete(value: boolean): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ONBOARDING_KEY, value ? "true" : "false");
  window.dispatchEvent(new Event("aura:onboarding-changed"));
}

export function clearOnboardingComplete(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ONBOARDING_KEY);
  window.dispatchEvent(new Event("aura:onboarding-changed"));
}
