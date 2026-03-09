from dataclasses import dataclass


@dataclass(slots=True)
class GeneratedTemplate:
    package: str
    files: dict[str, str]


def _base_files(*, title: str, brief_en: str, brief_ar: str) -> dict[str, str]:
    return {
        "README.md": f"# {title}\n\nGenerated landing page scaffold.\n",
        "content/brief.md": (
            "# Project Brief\n\n"
            f"## English\n{brief_en.strip()}\n\n"
            f"## Arabic\n{brief_ar.strip()}\n"
        ),
        "src/main.tsx": "export const appName = 'landing-page';\n",
    }


def _package_files(package: str) -> dict[str, str]:
    if package == "starter":
        return {
            "src/sections/hero.tsx": "export const heroVariant = 'starter';\n",
        }
    if package == "growth":
        return {
            "src/sections/hero.tsx": "export const heroVariant = 'growth';\n",
            "src/sections/social-proof.tsx": "export const socialProof = true;\n",
        }
    if package == "premium":
        return {
            "src/sections/hero.tsx": "export const heroVariant = 'premium';\n",
            "src/sections/social-proof.tsx": "export const socialProof = true;\n",
            "src/sections/pricing.tsx": "export const pricingEnabled = true;\n",
            "src/sections/faq.tsx": "export const faqEnabled = true;\n",
        }
    raise ValueError("Unsupported package")


def generate_template(*, package: str, title: str, brief_en: str, brief_ar: str) -> GeneratedTemplate:
    files = _base_files(title=title, brief_en=brief_en, brief_ar=brief_ar)
    files.update(_package_files(package))
    return GeneratedTemplate(package=package, files=files)
