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

  return (
    <main className="min-h-screen bg-gray-50 p-10">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold">
          Autonomous Job Automation Agent
        </h1>

        <p className="mt-2 text-gray-600">
          Candidate Dashboard
        </p>

        {loading ? (
          <p className="mt-8">Loading candidate...</p>
        ) : candidate ? (
          <div className="mt-8 rounded-xl bg-white p-6 shadow">
            <h2 className="text-2xl font-semibold">
              {candidate.full_name}
            </h2>

            <div className="mt-4 space-y-2">
              <p>
                <strong>Email:</strong> {candidate.email}
              </p>

              <p>
                <strong>Phone:</strong> {candidate.phone}
              </p>

              <p>
                <strong>Location:</strong> {candidate.location}
              </p>

              <p>
                <strong>Experience:</strong>{" "}
                {candidate.experience_years} years
              </p>

              <p>
                <strong>Target Roles:</strong>{" "}
                {candidate.target_titles}
              </p>

              <p>
                <strong>Skills:</strong> {candidate.skills}
              </p>
            </div>
          </div>
        ) : (
          <p className="mt-8 text-red-600">
            Could not load candidate data.
          </p>
        )}
      </div>
    </main>
  );
}