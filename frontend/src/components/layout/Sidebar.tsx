"use client";

import { useState } from "react";
import { Plus, X, FolderOpen } from "lucide-react";
import { useProjects, revalidateProjects } from "@/lib/hooks";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { cn } from "@/lib/utils";

interface SidebarProps {
  selectedId: string | null;
  onSelect: (id: string) => void;
  open: boolean;
  onClose: () => void;
}

export function Sidebar({ selectedId, onSelect, open, onClose }: SidebarProps) {
  const { data: projects = [], isLoading } = useProjects();
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [productName, setProductName] = useState("");
  const [creating, setCreating] = useState(false);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    try {
      const p = await api.projects.create({
        name: name.trim(),
        product_name: productName.trim() || name.trim(),
      });
      await revalidateProjects();
      setName("");
      setProductName("");
      setShowForm(false);
      onSelect(p.id);
      toast("Project created", "ok");
    } catch (err: unknown) {
      toast(err instanceof Error ? err.message : "Failed to create project", "err");
    } finally {
      setCreating(false);
    }
  }

  return (
    <>
      {open && (
        <div
          onClick={onClose}
          className="lg:hidden fixed inset-0 z-30 bg-black/60 backdrop-blur-sm"
        />
      )}
      <aside
        className={cn(
          "w-[260px] shrink-0 border-r border-[#2a2f3a] bg-[#171a21] flex flex-col overflow-hidden",
          "fixed inset-y-0 left-0 z-40 transition-transform duration-300 lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#2a2f3a]">
        <h2 className="text-[12px] font-bold text-[#9aa3b2] uppercase tracking-widest">Projects</h2>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="w-6 h-6 flex items-center justify-center rounded-md text-[#9aa3b2] hover:bg-[#1e222b] hover:text-[#e7e9ee] transition-colors"
          title="New project"
        >
          {showForm ? <X size={14} /> : <Plus size={14} />}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="px-4 py-3 border-b border-[#2a2f3a] bg-[#1e222b] flex flex-col gap-2"
        >
          <Input
            label="Project name"
            placeholder="Spotify"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <Input
            label="Product name"
            placeholder="Spotify"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
          />
          <div className="flex gap-2 pt-1">
            <Button type="submit" variant="primary" size="sm" loading={creating} className="flex-1">
              Create
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
          </div>
        </form>
      )}

      <div className="flex-1 overflow-y-auto px-2 py-2">
        {isLoading && (
          <p className="text-[12px] text-[#9aa3b2] px-2 py-2">Loading…</p>
        )}
        {!isLoading && projects.length === 0 && (
          <div className="px-2 py-4 text-center">
            <FolderOpen size={28} className="mx-auto mb-2 text-[#2a2f3a]" />
            <p className="text-[12px] text-[#9aa3b2]">No projects yet.</p>
            <p className="text-[11px] text-[#9aa3b2] mt-0.5">Click + to create one.</p>
          </div>
        )}
        {projects.map((p) => (
          <button
            key={p.id}
            onClick={() => { onSelect(p.id); onClose(); }}
            className={cn(
              "w-full text-left px-3 py-2.5 rounded-lg mb-1 transition-all group",
              selectedId === p.id
                ? "bg-[#1e222b] border border-[#2a2f3a] text-[#e7e9ee]"
                : "text-[#9aa3b2] hover:bg-[#1e222b] hover:text-[#e7e9ee] border border-transparent"
            )}
          >
            <div className="text-[13px] font-semibold truncate">{p.name}</div>
            <div className="text-[11px] text-[#9aa3b2] truncate mt-0.5">{p.product_name}</div>
          </button>
        ))}
      </div>
      </aside>
    </>
  );
}
