import React, { useEffect, useState } from "react";
import API from "../api/api";

const CertificatePage = () => {
  const [certificate, setCertificate] = useState(null);

  useEffect(() => {
    API.get("/certificate/").then((res) => setCertificate(res.data));
  }, []);

  if (!certificate) return <div>No certificate available</div>;

  return (
    <div>
      <h1>🎓 Congratulations!</h1>
      <img src={certificate.image_url} alt="Certificate" />
      <a href={certificate.image_url} download>
        Download PDF
      </a>
    </div>
  );
};

export default CertificatePage;
