"use client";

import {
  ChangeEvent,
  DragEvent,
  FormEvent,
  useMemo,
  useRef,
  useState,
} from "react";

import styles from "./SecureUploadPortal.module.css";

type UploadStatus = "idle" | "uploading" | "success" | "error";

const MAX_FILES = 20;
const MAX_FILE_SIZE = 250 * 1024 * 1024;

const acceptedFileTypes = [
  ".pdf",
  ".doc",
  ".docx",
  ".ppt",
  ".pptx",
  ".xls",
  ".xlsx",
  ".csv",
  ".txt",
  ".md",
  ".rtf",
  ".mp4",
  ".mov",
  ".webm",
  ".mp3",
  ".wav",
  ".m4a",
  ".jpg",
  ".jpeg",
  ".png",
  ".webp",
];

const contentCategories = [
  {
    label: "Documents",
    formats: "PDF · WORD · TEXT · MARKDOWN",
  },
  {
    label: "Presentations",
    formats: "POWERPOINT · SLIDES",
  },
  {
    label: "Data",
    formats: "EXCEL · CSV · TABLES",
  },
  {
    label: "Video",
    formats: "MP4 · MOV · WEBM",
  },
  {
    label: "Audio",
    formats: "MP3 · WAV · M4A",
  },
  {
    label: "Images",
    formats: "JPG · PNG · WEBP",
  },
];

function formatFileSize(size: number) {
  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function fileKey(file: File) {
  return `${file.name}-${file.size}-${file.lastModified}`;
}

export default function SecureUploadPortal() {
  const inputRef = useRef<HTMLInputElement>(null);

  const [files, setFiles] = useState<File[]>([]);
  const [objective, setObjective] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [businessType, setBusinessType] = useState("academy");
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [message, setMessage] = useState("");

  const totalSize = useMemo(
    () => files.reduce((total, file) => total + file.size, 0),
    [files],
  );

  function addFiles(incomingFiles: File[]) {
    setMessage("");
    setStatus("idle");

    const validFiles = incomingFiles.filter((file) => {
      if (file.size > MAX_FILE_SIZE) {
        setMessage(`${file.name} is larger than the 250 MB upload limit.`);
        return false;
      }

      return true;
    });

    setFiles((currentFiles) => {
      const existingKeys = new Set(currentFiles.map(fileKey));

      const newFiles = validFiles.filter(
        (file) => !existingKeys.has(fileKey(file)),
      );

      return [...currentFiles, ...newFiles].slice(0, MAX_FILES);
    });
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    addFiles(Array.from(event.target.files ?? []));
    event.target.value = "";
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    addFiles(Array.from(event.dataTransfer.files));
  }

  function removeFile(indexToRemove: number) {
    setFiles((currentFiles) =>
      currentFiles.filter((_, index) => index !== indexToRemove),
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (files.length === 0 && !websiteUrl.trim() && !objective.trim()) {
      setStatus("error");
      setMessage(
        "Add at least one file, website, or written description before starting.",
      );
      return;
    }

    setStatus("uploading");
    setMessage("Preparing your private knowledge workspace...");

    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    formData.append("objective", objective.trim());
    formData.append("website_url", websiteUrl.trim());
    formData.append("business_type", businessType);

    try {
      const response = await fetch("/api/knowledge/upload", {
        method: "POST",
        credentials: "include",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed.");
      }

      const result = (await response.json()) as {
        message?: string;
      };

      setStatus("success");
      setMessage(
        result.message ??
          "Your files were received. The Knowledge Engine is preparing your business blueprint.",
      );
    } catch {
      setStatus("error");
      setMessage(
        "The portal interface is working, but the secure backend upload endpoint is not connected yet.",
      );
    }
  }

  return (
    <div className={styles.portal}>
      <div className={styles.portalHeader}>
        <div>
          <span className={styles.portalIndex}>Secure intake / 001</span>
          <h2>Build from what you already have.</h2>
        </div>

        <span className={styles.securityStatus}>
          <span className={styles.securityDot} />
          Private workspace
        </span>
      </div>

      <p className={styles.portalIntroduction}>
        Upload your documents, lessons, research, recordings, presentations,
        worksheets, videos, and existing business material. The Knowledge
        Engine™ organizes the source material into an academy, curriculum,
        offers, and operating plan.
      </p>

      <div className={styles.categoryGrid}>
        {contentCategories.map((category) => (
          <div className={styles.category} key={category.label}>
            <strong>{category.label}</strong>
            <span>{category.formats}</span>
          </div>
        ))}
      </div>

      <form className={styles.form} onSubmit={handleSubmit}>
        <div
          className={styles.dropZone}
          onDragEnter={(event) => event.preventDefault()}
          onDragOver={(event) => event.preventDefault()}
          onDrop={handleDrop}
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              inputRef.current?.click();
            }
          }}
        >
          <input
            ref={inputRef}
            className={styles.fileInput}
            type="file"
            accept={acceptedFileTypes.join(",")}
            multiple
            onChange={handleFileChange}
          />

          <span className={styles.uploadSymbol}>＋</span>

          <div>
            <strong>Drop your knowledge here</strong>
            <span>or click to securely select files</span>
          </div>

          <span className={styles.uploadLimit}>
            Up to {MAX_FILES} files · 250 MB each
          </span>
        </div>

        {files.length > 0 && (
          <div className={styles.fileQueue}>
            <div className={styles.fileQueueHeader}>
              <span>Selected sources</span>
              <span>
                {files.length} files · {formatFileSize(totalSize)}
              </span>
            </div>

            {files.map((file, index) => (
              <div className={styles.fileRow} key={fileKey(file)}>
                <div>
                  <strong>{file.name}</strong>
                  <span>{formatFileSize(file.size)}</span>
                </div>

                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  aria-label={`Remove ${file.name}`}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}

        <div className={styles.inputGrid}>
          <label className={styles.field}>
            <span>What are you building?</span>

            <select
              value={businessType}
              onChange={(event) => setBusinessType(event.target.value)}
            >
              <option value="academy">Online academy</option>
              <option value="course-business">Course business</option>
              <option value="membership">Membership community</option>
              <option value="certification">Certification program</option>
              <option value="coaching">Coaching or consulting business</option>
              <option value="training-company">Training company</option>
              <option value="knowledge-platform">Knowledge platform</option>
            </select>
          </label>

          <label className={styles.field}>
            <span>Existing website</span>

            <input
              type="url"
              value={websiteUrl}
              onChange={(event) => setWebsiteUrl(event.target.value)}
              placeholder="https://yourwebsite.com"
            />
          </label>
        </div>

        <label className={styles.field}>
          <span>Describe your objective</span>

          <textarea
            value={objective}
            onChange={(event) => setObjective(event.target.value)}
            placeholder="I want to turn my experience, presentations, and training videos into a complete technology academy."
          />
        </label>

        <div className={styles.securityGrid}>
          <div>
            <strong>Encrypted transfer</strong>
            <span>Files must travel through HTTPS/TLS.</span>
          </div>

          <div>
            <strong>Malware screening</strong>
            <span>Every source must be quarantined and scanned.</span>
          </div>

          <div>
            <strong>Tenant isolation</strong>
            <span>Organizations must never access one another’s files.</span>
          </div>

          <div>
            <strong>Controlled processing</strong>
            <span>Only approved source material enters the engine.</span>
          </div>
        </div>

        <div className={styles.formFooter}>
          <div className={styles.formStatus} aria-live="polite">
            <span>
              {status === "uploading"
                ? "Preparing secure intake"
                : "Knowledge Engine™ ready"}
            </span>

            {message && (
              <p
                className={
                  status === "error"
                    ? styles.errorMessage
                    : styles.statusMessage
                }
              >
                {message}
              </p>
            )}
          </div>

          <button
            className={styles.buildButton}
            type="submit"
            disabled={status === "uploading"}
          >
            <span>
              {status === "uploading"
                ? "Uploading..."
                : "Build my business"}
            </span>

            <span aria-hidden="true">→</span>
          </button>
        </div>
      </form>
    </div>
  );
}