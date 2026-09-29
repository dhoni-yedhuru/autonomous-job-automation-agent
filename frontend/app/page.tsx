"use client";

import { useEffect, useState } from "react";

type Candidate = {
  id: number;
  full_name: string;
  email: string;
  phone: string | null;
  location: string | null;
  experience_years: number;
  target_titles: string | null;
  skills: string | null;
  master_resume: string | null;
};

export default function Home() {
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/candidates/3")
      .then((response) => response.json())
      .then((data) => {
        setCandidate(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const handleChange = (
    field: keyof Candidate,
    value: string | number
  ) => {
    if (!candidate) return;

    setCandidate({
      ...candidate,
      [field]: value,
    });
  };

  const handleSave = async () => {
    if (!candidate) return;

    setSaving(true);
    setMessage("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/candidates/${candidate.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(candidate),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage("Failed to save profile.");
        return;
      }

      setCandidate(data);
      setMessage("Profile saved successfully.");
    } catch {
      setMessage("Could not connect to backend.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-10">
        <p>Loading candidate...</p>
      </main>
    );
  }

  if (!candidate) {
    return (
      <main className="min-h-screen bg-gray-50 p-10">
        <p className="text-red-600">
          Could not load candidate data.
        </p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-10">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold">
          Autonomous Job Automation Agent
        </h1>

        <p className="mt-2 text-gray-600">
          Candidate Profile
        </p>

        <div className="mt-8 rounded-xl bg-white p-6 shadow">
          <div className="grid gap-5 md:grid-cols-2">

            <div>
              <label className="font-medium">
                Full Name
              </label>
              <input
                className="mt-2 w-full rounded-lg border p-3"
                value={candidate.full_name}
                onChange={(e) =>
                  handleChange("full_name", e.target.value)
                }
              />
            </div>

            <div>
              <label className="font-medium">
                Email
              </label>
              <input
                type="email"
                className="mt-2 w-full rounded-lg border p-3"
                value={candidate.email}
                onChange={(e) =>
                  handleChange("email", e.target.value)
                }
              />
            </div>

            <div>
              <label className="font-medium">
                Phone
              </label>
              <input
                className="mt-2 w-full rounded-lg border p-3"
                value={candidate.phone ?? ""}
                onChange={(e) =>
                  handleChange("phone", e.target.value)
                }
              />
            </div>

            <div>
              <label className="font-medium">
                Location
              </label>
              <input
                className="mt-2 w-full rounded-lg border p-3"
                value={candidate.location ?? ""}
                onChange={(e) =>
                  handleChange("location", e.target.value)
                }
              />
            </div>

            <div>
              <label className="font-medium">
                Experience (Years)
              </label>
              <input
                type="number"
                min="0"
                className="mt-2 w-full rounded-lg border p-3"
                value={candidate.experience_years}
                onChange={(e) =>
                  handleChange(
                    "experience_years",
                    Number(e.target.value)
                  )
                }
              />
            </div>

            <div>
              <label className="font-medium">
                Target Job Titles
              </label>
              <input
                className="mt-2 w-full rounded-lg border p-3"
                value={candidate.target_titles ?? ""}
                onChange={(e) =>
                  handleChange("target_titles", e.target.value)
                }
              />
            </div>

            <div className="md:col-span-2">
              <label className="font-medium">
                Skills
              </label>
              <textarea
                className="mt-2 w-full rounded-lg border p-3"
                rows={3}
                value={candidate.skills ?? ""}
                onChange={(e) =>
                  handleChange("skills", e.target.value)
                }
              />
            </div>

            <div className="md:col-span-2">
              <label className="font-medium">
                Master Resume
              </label>
              <textarea
                className="mt-2 w-full rounded-lg border p-3"
                rows={10}
                value={candidate.master_resume ?? ""}
                onChange={(e) =>
                  handleChange("master_resume", e.target.value)
                }
              />
            </div>
          </div>

          <div className="mt-6 flex items-center gap-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="rounded-lg bg-black px-6 py-3 font-medium text-white disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Profile"}
            </button>

            {message && (
              <p className="text-sm text-gray-600">
                {message}
              </p>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}