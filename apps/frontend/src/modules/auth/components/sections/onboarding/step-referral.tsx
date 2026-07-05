import { ChangeEvent } from "react";
import { ArrowRight } from "lucide-react";
import { Button } from "@/shared/components/ui/button";

import LinkedinIcon from "../../../../../../public/assets/icons/linkedin";
import InstagramIcon from "../../../../../../public/assets/icons/instagram";
import ChatgptIcon from "../../../../../../public/assets/icons/chatgpt";
import OthersIcon from "../../../../../../public/assets/icons/others";

interface StepReferralProps {
  referralSource: string;
  setReferralSource: (source: string) => void;
  onContinue: () => void;
  onSkip: () => void;
  isSubmitting: boolean;
}

export default function StepReferral({
  referralSource,
  setReferralSource,
  onContinue,
  onSkip,
  isSubmitting,
}: StepReferralProps) {
  const isOthersSelected = referralSource === "Others" || referralSource.startsWith("Others:");

  const otherText = referralSource.startsWith("Others:") ? referralSource.substring(7) : "";

  const handleOtherTextChange = (e: ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    if (val.trim() === "") {
      setReferralSource("Others");
    } else {
      setReferralSource(`Others:${val}`);
    }
  };

  const isValid =
    referralSource !== "" &&
    (!isOthersSelected || (referralSource.startsWith("Others:") && referralSource.substring(7).trim() !== ""));

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-300 w-full max-w-md">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 md:text-3xl">
          Where did you hear about us?
        </h1>
        <p className="text-[15px] text-slate-500">
          Help us learn where you found us. We appreciate your feedback!
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* LinkedIn */}
        <button
          type="button"
          onClick={() => setReferralSource("LinkedIn")}
          className={`relative flex items-center gap-3 rounded-xl border p-4 text-left transition-all duration-350 cursor-pointer ${
            referralSource === "LinkedIn"
              ? "border-[#0A66C2] bg-[#0A66C2]/5 ring-1 ring-[#0A66C2]"
              : "border-slate-200 bg-white hover:border-[#0A66C2]/30"
          }`}
        >
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg transition-colors duration-300 ${
              referralSource === "LinkedIn"
                ? "bg-[#0A66C2] text-white"
                : "bg-[#0A66C2]/10 text-[#0A66C2]"
            }`}
          >
            <LinkedinIcon width={18} height={18} />
          </div>
          <span className="font-semibold text-slate-800 text-sm">LinkedIn</span>
        </button>

        {/* ChatGPT */}
        <button
          type="button"
          onClick={() => setReferralSource("ChatGPT")}
          className={`relative flex items-center gap-3 rounded-xl border p-4 text-left transition-all duration-350 cursor-pointer ${
            referralSource === "ChatGPT"
              ? "border-[#10A37F] bg-[#10A37F]/5 ring-1 ring-[#10A37F]"
              : "border-slate-200 bg-white hover:border-[#10A37F]/30"
          }`}
        >
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg transition-colors duration-300 ${
              referralSource === "ChatGPT"
                ? "bg-[#10A37F] text-white"
                : "bg-[#10A37F]/10 text-[#10A37F]"
            }`}
          >
            <ChatgptIcon width={18} height={18} />
          </div>
          <span className="font-semibold text-slate-800 text-sm">ChatGPT</span>
        </button>

        {/* Instagram */}
        <button
          type="button"
          onClick={() => setReferralSource("Instagram")}
          className={`relative flex items-center gap-3 rounded-xl border p-4 text-left transition-all duration-350 cursor-pointer ${
            referralSource === "Instagram"
              ? "border-[#D6249F] bg-[#D6249F]/5 ring-1 ring-[#D6249F]"
              : "border-slate-200 bg-white hover:border-[#D6249F]/30"
          }`}
        >
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg transition-all duration-300 ${
              referralSource === "Instagram"
                ? "bg-gradient-to-tr from-[#fdf497] via-[#fd5949] to-[#d6249f] text-white"
                : "bg-[#d6249f]/10 text-[#d6249f]"
            }`}
          >
            <InstagramIcon width={18} height={18} />
          </div>
          <span className="font-semibold text-slate-800 text-sm">Instagram</span>
        </button>

        {/* Others */}
        <button
          type="button"
          onClick={() => setReferralSource("Others")}
          className={`relative flex items-center gap-3 rounded-xl border p-4 text-left transition-all duration-350 cursor-pointer ${
            isOthersSelected
              ? "border-[#7C3AED] bg-[#7C3AED]/5 ring-1 ring-[#7C3AED]"
              : "border-slate-200 bg-white hover:border-[#7C3AED]/30"
          }`}
        >
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg transition-colors duration-300 ${
              isOthersSelected
                ? "bg-[#7C3AED] text-white"
                : "bg-[#7C3AED]/10 text-[#7C3AED]"
            }`}
          >
            <OthersIcon width={18} height={18} />
          </div>
          <span className="font-semibold text-slate-800 text-sm">Others</span>
        </button>
      </div>

      {isOthersSelected && (
        <div className="flex flex-col gap-2 animate-in fade-in slide-in-from-top-2 duration-300">
          <label htmlFor="other-source-input" className="text-sm font-semibold text-slate-750">
            What others? Please specify:
          </label>
          <input
            id="other-source-input"
            type="text"
            value={otherText}
            onChange={handleOtherTextChange}
            placeholder="Friend, Google Search, Newsletter..."
            className="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 placeholder-slate-400 outline-none transition-all duration-200 focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED]"
            autoFocus
          />
        </div>
      )}

      <div className="flex flex-col gap-3">
        <Button
          onClick={onContinue}
          disabled={!isValid || isSubmitting}
          className={`h-12 w-full rounded-full text-[15px] font-semibold text-white shadow-none transition-all duration-300 ${
            isValid && !isSubmitting
              ? "bg-primary hover:bg-primary-hover hover:shadow-lg cursor-pointer"
              : "bg-slate-200/80 text-slate-400 opacity-25 cursor-not-allowed pointer-events-none"
          }`}
        >
          {isSubmitting ? "Completing setup..." : "Complete Setup"}
        </Button>

        <button
          onClick={onSkip}
          disabled={isSubmitting}
          className="flex items-center justify-center gap-1.5 py-2 text-sm font-semibold text-slate-500 hover:text-slate-900 transition-colors duration-200 cursor-pointer self-center disabled:opacity-40"
        >
          Skip for now <ArrowRight size={14} />
        </button>
      </div>
    </div>
  );
}
