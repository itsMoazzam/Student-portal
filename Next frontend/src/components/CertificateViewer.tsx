export default function CertificateViewer({ url }: { url: string }) {
  return (
    <div className="mt-4">
      <iframe
        src={url}
        title="Certificate"
        width="100%"
        height="600px"
        className="border border-gray-300"
      />
    </div>
  );
}
