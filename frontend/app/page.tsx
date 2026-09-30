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

type Job = {
  id: number;
  title: string;
  company: string;
  location: string | null;
  job_url: string | null;
  source: string | null;
  description: string | null;
  required_skills: string | null;
  salary: string | null;
  work_mode: string | null;
  posted_date: string | null;
  status: string;
  match_score: number;
};

export default function Home() {
  const [discovering, setDiscovering] = useState(false);
  const [discoverMessage, setDiscoverMessage] = useState("");

  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    Promise.all([
      fetch("http://127.0.0.1:8000/candidates/3").then((res) =>
        res.json()
      ),
      fetch("http://127.0.0.1:8000/jobs").then((res) =>
        res.json()
      ),
    ])
      .then(([candidateData, jobsData]) => {
        setCandidate(candidateData);
        setJobs(jobsData);
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

  const handleDiscoverJobs = async () => {
  setDiscovering(true);
  setDiscoverMessage("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/jobs/discover",
      {
        method: "POST",
      }
    );

    const data = await response.json();

    if (!response.ok) {
      setDiscoverMessage("Job discovery failed.");
      return;
    }

    setDiscoverMessage(
      `${data.new_jobs} new job(s) discovered.`
    );

    const jobsResponse = await fetch(
      "http://127.0.0.1:8000/jobs"
    );

    const jobsData = await jobsResponse.json();

    setJobs(jobsData);
  } catch {
    setDiscoverMessage(
      "Could not connect to backend."
    );
  } finally {
    setDiscovering(false);
  }
};

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-10">
        <p>Loading dashboard...</p>
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
      <div className="mx-auto max-w-6xl">

        <h1 className="text-3xl font-bold">
          Autonomous Job Automation Agent
        </h1>

        <p className="mt-2 text-gray-600">
          Candidate Dashboard
        </p>

        {/* Candidate Profile */}

        <section className="mt-8 rounded-xl bg-white p-6 shadow">
          <h2 className="text-2xl font-semibold">
            Candidate Profile
          </h2>

          <div className="mt-6 grid gap-5 md:grid-cols-2">

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
                rows={8}
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
        </section>

        {/* Jobs */}

        <section className="mt-8">

          <h2 className="text-2xl font-semibold">
            Jobs
          </h2>

          <div className="mt-4 flex items-center gap-4">
            <button
              onClick={handleDiscoverJobs}
              disabled={discovering}
              className="rounded-lg bg-black px-5 py-3 font-medium text-white disabled:opacity-50"
            >
              {discovering ? "Discovering..." : "Discover Jobs"}
            </button>

            {discoverMessage && (
              <p className="text-sm text-gray-600">
                {discoverMessage}
              </p>
            )}
          </div>

          <p className="mt-2 text-gray-600">
            Jobs currently stored in the system
          </p>

          {jobs.length === 0 ? (
            <div className="mt-6 rounded-xl bg-white p-6 shadow">
              <p>No jobs found.</p>
            </div>
          ) : (
            <div className="mt-6 space-y-5">

              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="rounded-xl bg-white p-6 shadow"
                >

                  <div className="flex flex-col justify-between gap-4 md:flex-row">

                    <div>

                      <h3 className="text-xl font-semibold">
                        {job.title}
                      </h3>

                      <p className="mt-1 font-medium text-gray-700">
                        {job.company}
                      </p>

                      <div className="mt-3 space-y-1 text-sm text-gray-600">

                        <p>
                          <strong>Location:</strong>{" "}
                          {job.location || "Not specified"}
                        </p>

                        <p>
                          <strong>Work Mode:</strong>{" "}
                          {job.work_mode || "Not specified"}
                        </p>

                        <p>
                          <strong>Salary:</strong>{" "}
                          {job.salary || "Not specified"}
                        </p>

                        <p>
                          <strong>Source:</strong>{" "}
                          {job.source || "Unknown"}
                        </p>

                        <p>
                          <strong>Status:</strong>{" "}
                          {job.status}
                        </p>

			<p>
 			 <strong>Match Score:</strong>{" "}
  				{job.match_score}%
			</p>
				
                      </div>

                    </div>

                    <div className="flex items-start">

                      {job.job_url && (
                        <a
                          href={job.job_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="rounded-lg border px-4 py-2 font-medium hover:bg-gray-50"
                        >
                          View Job
                        </a>
                      )}

                    </div>


                    <button
                      onClick={async () => {
                        const response = await fetch(
                          `http://127.0.0.1:8000/jobs/${job.id}/latex-resume/3`
                        );

                        const data = await response.json();

                        const blob = new Blob([data.latex], {
                            type: "application/x-tex",
                          });

                          const url = URL.createObjectURL(blob);

                          const link = document.createElement("a");
                          link.href = url;
                          link.download = `${job.title.replace(/\s+/g, "_")}_Resume.tex`;
                          link.click();

                          URL.revokeObjectURL(url);
                      }}
                      className="rounded-lg bg-black px-4 py-2 font-medium text-white"
                    >
                      Generate LaTeX Resume
                    </button>

                  </div>

                  {job.required_skills && (
                    <div className="mt-5">

                      <p className="font-medium">
                        Required Skills
                      </p>

                      <p className="mt-1 text-gray-600">
                        {job.required_skills}
                      </p>

                    </div>
                  )}

                  {job.description && (
                    <div className="mt-5">

                      <p className="font-medium">
                        Description
                      </p>

                      <p className="mt-1 text-gray-600">
                        {job.description}
                      </p>

                    </div>
                  )}

                </div>
              ))}

            </div>
          )}

        </section>

      </div>
    </main>
  );
}