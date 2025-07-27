import { useEffect, useState } from "react";
import { API } from "../api";

export default function CustomerTable() {
  const [rows, setRows] = useState([]);
  const [editing, setEditing] = useState(null);

  const load = async () => {
    const { data } = await API.get("/customers");
    setRows(data);
  };

  useEffect(() => {
    load();
  }, []);

  const remove = async (id) => {
    if (!confirm(`Delete customer ${id}?`)) return;
    await API.delete(`/customers/${id}`);
    load();
  };

  const startEdit = (row) => setEditing(row);
  const cancelEdit = () => setEditing(null);

  const saveEdit = async () => {
    const { id, ...rest } = editing;
    await API.put(`/customers/${id}`, rest);
    setEditing(null);
    load();
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Customers</h2>
        <button className="btn" onClick={load}>Refresh</button>
      </div>

      <table className="table">
        <thead>
          <tr className="border-b">
            <th className="py-2">ID</th>
            <th className="py-2">Name</th>
            <th className="py-2">Phone</th>
            <th className="py-2">Address</th>
            <th className="py-2 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-b">
              <td className="py-2">{r.id}</td>
              <td className="py-2">{r.name}</td>
              <td className="py-2">{r.phone}</td>
              <td className="py-2">{r.address}</td>
              <td className="py-2 text-right space-x-2">
                <button className="btn" onClick={() => startEdit(r)}>Edit</button>
                <button className="btn bg-red-600 hover:bg-red-700" onClick={() => remove(r.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {editing && (
        <div className="mt-4 border-t pt-4">
          <h3 className="font-semibold mb-2">Editing ID #{editing.id}</h3>
          <div className="space-y-2">
            <input
              className="input"
              value={editing.name}
              onChange={(e) => setEditing({ ...editing, name: e.target.value })}
            />
            <input
              className="input"
              value={editing.phone}
              onChange={(e) => setEditing({ ...editing, phone: e.target.value })}
            />
            <input
              className="input"
              value={editing.address}
              onChange={(e) => setEditing({ ...editing, address: e.target.value })}
            />
            <div className="flex gap-2">
              <button className="btn" onClick={saveEdit}>Save</button>
              <button className="btn bg-gray-400 hover:bg-gray-500" onClick={cancelEdit}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
