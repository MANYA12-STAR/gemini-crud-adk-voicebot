import { useState } from "react";
import { API } from "../api";

export default function CustomerForm({ onCreated }) {
  const [form, setForm] = useState({ name: "", phone: "", address: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const validateForm = () => {
    const phonePattern = /^\+?[0-9]{10,15}$/;
    if (!form.name.trim() || !form.phone.trim() || !form.address.trim()) {
      return "All fields are required.";
    }
    if (!phonePattern.test(form.phone)) {
      return "Phone number must be 10–15 digits, optionally starting with +.";
    }
    return "";
  };

  const submit = async (e) => {
    e.preventDefault();
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const { data } = await API.post("/customers", form);
      onCreated?.(data);
      setForm({ name: "", phone: "", address: "" });
    } catch (err) {
      setError("Failed to create customer. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Create Customer (Form)</h2>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <form onSubmit={submit} className="space-y-3">
        <input
          className="input"
          placeholder="Name"
          value={form.name}
          onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
        />
        <input
          className="input"
          placeholder="Phone (e.g., +919999999999)"
          value={form.phone}
          onChange={(e) => setForm(f => ({ ...f, phone: e.target.value }))}
        />
        <input
          className="input"
          placeholder="Address"
          value={form.address}
          onChange={(e) => setForm(f => ({ ...f, address: e.target.value }))}
        />
        <button className="btn" disabled={loading}>
          {loading ? "Creating..." : "Create"}
        </button>
      </form>
    </div>
  );
}
