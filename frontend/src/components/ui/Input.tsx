import { cn } from "@/lib/utils";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className, id, ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={id} className="text-[11px] font-semibold text-[#9aa3b2] uppercase tracking-wider">
          {label}
        </label>
      )}
      <input
        id={id}
        className={cn(
          "w-full px-3 py-2 bg-[#1e222b] border border-[#2a2f3a] rounded-lg",
          "text-[#e7e9ee] text-[13px] placeholder:text-[#9aa3b2]",
          "focus:outline-none focus:border-[#5b8cff] transition-colors",
          error && "border-[#f87171]",
          className
        )}
        {...props}
      />
      {error && <p className="text-[11px] text-[#f87171]">{error}</p>}
    </div>
  );
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
}

export function Textarea({ label, className, id, ...props }: TextareaProps) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={id} className="text-[11px] font-semibold text-[#9aa3b2] uppercase tracking-wider">
          {label}
        </label>
      )}
      <textarea
        id={id}
        className={cn(
          "w-full px-3 py-2 bg-[#1e222b] border border-[#2a2f3a] rounded-lg resize-y",
          "text-[#e7e9ee] text-[12px] font-mono placeholder:text-[#9aa3b2]",
          "focus:outline-none focus:border-[#5b8cff] transition-colors",
          className
        )}
        {...props}
      />
    </div>
  );
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string; label: string }[];
}

export function Select({ label, options, className, id, ...props }: SelectProps) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={id} className="text-[11px] font-semibold text-[#9aa3b2] uppercase tracking-wider">
          {label}
        </label>
      )}
      <select
        id={id}
        className={cn(
          "w-full px-3 py-2 bg-[#1e222b] border border-[#2a2f3a] rounded-lg",
          "text-[#e7e9ee] text-[13px]",
          "focus:outline-none focus:border-[#5b8cff] transition-colors cursor-pointer",
          className
        )}
        {...props}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}
