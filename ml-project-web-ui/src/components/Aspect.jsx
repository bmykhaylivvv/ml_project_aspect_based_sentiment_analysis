import React from "react";

import styles from "./aspect.module.css";

export default function Aspect(props) {
  const { name, descriptions } = props;

  return (
    <div className={styles.aspectsBlock}>
      <div className={styles.aspectsName}>{name}</div>
      <div className={styles.aspectsDescription}>{descriptions.join(', ')}</div>
    </div>
  );
}
